import json
import logging
import re
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from db import check_db_connection, get_db
from embedder import embed
from steam_fetcher import fetch_steam_detail, fetch_steamspy, parse_release_date


class HealthEndpointAccessFilter(logging.Filter):
    # 헬스 체크 요청은 정상 동작 중 반복 호출되므로 접근 로그에서만 제외한다.
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return "/health/live" not in message and "/health/ready" not in message


uvicorn_access_logger = logging.getLogger("uvicorn.access")
if not any(isinstance(existing_filter, HealthEndpointAccessFilter) for existing_filter in uvicorn_access_logger.filters):
    uvicorn_access_logger.addFilter(HealthEndpointAccessFilter())


app = FastAPI(title="gWeb2 Python Service", version="0.1.0")


@app.get("/health/live", status_code=200)
def live_health():
    return {
        "status": "UP",
        "service": "python-api",
    }


@app.get("/health/ready", status_code=200)
def ready_health():
    try:
        check_db_connection()
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "DOWN",
                "service": "python-api",
                "details": {
                    "database": "DOWN",
                    "reason": str(exc),
                },
            },
        )

    return {
        "status": "UP",
        "service": "python-api",
        "details": {
            "database": "UP",
        },
    }


# ── 요청/응답 모델 ──────────────────────────────────────────────────────────────

class FetchRequest(BaseModel):
    app_id: int


class AnalyzeRequest(BaseModel):
    query: str


class AnalyzeResponse(BaseModel):
    embedding: list[float]
    intent: str
    matched_game_ids: list[int]


# ── /fetch : Steam 데이터 수집 → DB 저장 ───────────────────────────────────────

@app.post("/fetch", status_code=200)
def fetch_game(req: FetchRequest, db: Session = Depends(get_db)):
    app_id = req.app_id

    # 이미 있으면 스킵
    exists = db.execute(
        text("SELECT 1 FROM games WHERE steam_appid = :id"), {"id": app_id}
    ).fetchone()
    if exists:
        return {"status": "already_exists"}

    # Steam API 호출
    detail = fetch_steam_detail(app_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Steam app {app_id} not found")

    spy = fetch_steamspy(app_id)

    # 기본 정보 파싱
    price_data = detail.get("price_overview", {})
    price_initial = price_data.get("initial")
    price_final = price_data.get("final")
    if price_initial is not None:
        price_initial = price_initial // 100
    if price_final is not None:
        price_final = price_final // 100
    release_raw = detail.get("release_date", {}).get("date")
    release_date = parse_release_date(release_raw)

    owners_str = spy.get("owners", "0 .. 0")
    owners_parts = [int(x.strip().replace(",", "")) for x in owners_str.split("..")]

    # 임베딩 생성
    name = detail.get("name", "")
    short_desc = detail.get("short_description", "")
    name_emb = embed(name)
    desc_emb = embed(short_desc) if short_desc else name_emb

    name_emb_str = "[" + ",".join(str(x) for x in name_emb) + "]"
    desc_emb_str = "[" + ",".join(str(x) for x in desc_emb) + "]"

    # games 테이블 저장
    result = db.execute(text("""
        INSERT INTO games (
            steam_appid, name, short_description, detailed_description,
            header_image, release_date, is_free,
            price_initial, price_final, metacritic_score, website,
            owners_min, owners_max,
            average_playtime_forever, median_playtime_forever,
            positive_reviews, negative_reviews,
            name_embedding, desc_embedding,
            data_fetched_at, last_updated_at
        ) VALUES (
            :appid, :name, :short_desc, :detail_desc,
            :header_image, :release_date, :is_free,
            :price_initial, :price_final, :metacritic, :website,
            :owners_min, :owners_max,
            :avg_playtime, :med_playtime,
            :positive, :negative,
            CAST(:name_emb AS vector), CAST(:desc_emb AS vector),
            NOW(), NOW()
        ) RETURNING id
    """), {
        "appid": app_id,
        "name": name,
        "short_desc": short_desc,
        "detail_desc": detail.get("detailed_description", ""),
        "header_image": detail.get("header_image", ""),
        "release_date": release_date,
        "is_free": detail.get("is_free", False),
        "price_initial": price_initial,
        "price_final": price_final,
        "metacritic": detail.get("metacritic", {}).get("score"),
        "website": detail.get("website", ""),
        "owners_min": owners_parts[0] if len(owners_parts) > 0 else None,
        "owners_max": owners_parts[1] if len(owners_parts) > 1 else None,
        "avg_playtime": spy.get("average_forever"),
        "med_playtime": spy.get("median_forever"),
        "positive": detail.get("recommendations", {}).get("total") or spy.get("positive"),
        "negative": spy.get("negative"),
        "name_emb": name_emb_str,
        "desc_emb": desc_emb_str,
    })
    game_id = result.fetchone()[0]

    # 장르 저장
    for g in detail.get("genres", []):
        db.execute(text("""
            INSERT INTO game_genres (game_id, genre_id, genre_name, source)
            VALUES (:gid, :genre_id, :genre_name, 'steam')
        """), {"gid": game_id, "genre_id": int(g["id"]), "genre_name": g["description"]})

    # 카테고리 저장
    for c in detail.get("categories", []):
        db.execute(text("""
            INSERT INTO game_categories (game_id, category_id, category_name)
            VALUES (:gid, :cid, :cname)
        """), {"gid": game_id, "cid": int(c["id"]), "cname": c["description"]})

    # 개발사/퍼블리셔 저장
    for dev in detail.get("developers", []):
        db.execute(text("""
            INSERT INTO game_actors (game_id, actor_name, actor_type)
            VALUES (:gid, :name, 'DEVELOPER')
        """), {"gid": game_id, "name": dev})

    for pub in detail.get("publishers", []):
        db.execute(text("""
            INSERT INTO game_actors (game_id, actor_name, actor_type)
            VALUES (:gid, :name, 'PUBLISHER')
        """), {"gid": game_id, "name": pub})

    # SteamSpy 태그 저장
    for tag_name, vote_count in (spy.get("tags") or {}).items():
        db.execute(text("""
            INSERT INTO game_tags (game_id, tag_name, vote_count)
            VALUES (:gid, :tag, :votes)
        """), {"gid": game_id, "tag": tag_name, "votes": vote_count})

    # document_chunks 저장 (설명 청크)
    if short_desc:
        chunk_emb_str = desc_emb_str
        db.execute(text("""
            INSERT INTO document_chunks (game_id, chunk_type, content, embedding)
            VALUES (:gid, 'GAME_DESCRIPTION', :content, CAST(:emb AS vector))
        """), {"gid": game_id, "content": short_desc, "emb": chunk_emb_str})

    db.commit()
    return {"status": "ok", "game_id": game_id}


# ── /analyze : 질의 벡터화 + 의미 추출 + 유사 게임 검색 ──────────────────────────

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_query(req: AnalyzeRequest, db: Session = Depends(get_db)):
    query_text = req.query

    # 1. 임베딩
    query_emb = embed(query_text)
    emb_str = "[" + ",".join(str(x) for x in query_emb) + "]"

    # 2. pgvector 유사도 검색 (desc_embedding 기준 상위 5개)
    vector_rows = db.execute(text("""
        SELECT id FROM games
        ORDER BY desc_embedding <=> CAST(:emb AS vector)
        LIMIT 5
    """), {"emb": emb_str}).fetchall()
    vector_ids = [r[0] for r in vector_rows]

    # 3. pg_trgm 키워드 검색 (단어 추출 후 이름/태그 유사도)
    words = re.findall(r'\w+', query_text)
    trgm_ids = []
    if words:
        keyword = " ".join(words[:5])
        trgm_rows = db.execute(text("""
            SELECT id FROM games
            WHERE similarity(name, :kw) > 0.15
            ORDER BY similarity(name, :kw) DESC
            LIMIT 5
        """), {"kw": keyword}).fetchall()
        trgm_ids = [r[0] for r in trgm_rows]

    # 중복 제거하여 합치기
    matched = list(dict.fromkeys(vector_ids + trgm_ids))[:10]

    # 4. 간단한 의도 추출 (단어 기반)
    intent = extract_intent(query_text)

    return AnalyzeResponse(
        embedding=query_emb,
        intent=intent,
        matched_game_ids=matched,
    )


def extract_intent(query: str) -> str:
    query_lower = query.lower()
    intents = []
    if any(w in query_lower for w in ["추천", "recommend", "좋은", "재미"]):
        intents.append("recommend")
    if any(w in query_lower for w in ["분석", "통계", "얼마나", "몇명"]):
        intents.append("analyze")
    if any(w in query_lower for w in ["리뷰", "평가", "review", "평점"]):
        intents.append("review")
    if any(w in query_lower for w in ["개발", "만들", "개발자", "도구"]):
        intents.append("development")
    return ",".join(intents) if intents else "general"
