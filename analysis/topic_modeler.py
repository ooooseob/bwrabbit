#!/usr/bin/env python3
"""topic_modeler — CSV 텍스트 컬럼 → LDA 주제 모델링 → 마크다운 리포트 + 문서별 주제 CSV.

읽기:  topic_modeler.json
입력:  ../../../data/<INPUT_FILENAME>
출력:  ../../../reports/<OUTPUT_FILENAME>  (리포트)
       ../../../data/<OUTPUT_CSV>          (dominant_topic 컬럼 추가 CSV)

외부 API 없음. scikit-learn LDA만 사용.
"""
import csv, json, os, sys

HERE        = os.path.dirname(os.path.abspath(__file__))
CFG_PATH    = os.path.join(HERE, "topic_modeler.json")
DATA_DIR    = os.path.normpath(os.path.join(HERE, "..", "..", "..", "data"))
REPORTS_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "reports"))

DEFAULTS = {
    "INPUT_FILENAME":  "multilingual_reviews.csv",
    "TEXT_COL":        "text",
    "N_TOPICS":        3,
    "N_TOP_WORDS":     10,
    "MAX_FEATURES":    500,
    "MAX_ITER":        20,
    "OUTPUT_FILENAME": "reviews_topics.md",
    "OUTPUT_CSV":      "reviews_topics.csv",
}


def detect_lang(texts, sample_n=50):
    try:
        from langdetect import detect
        from collections import Counter
    except ImportError:
        return "en"
    sample = [t for t in texts if len(t.strip()) > 10][:sample_n]
    langs = []
    for t in sample:
        try:
            langs.append(detect(t))
        except Exception:
            pass
    if not langs:
        return "en"
    return Counter(langs).most_common(1)[0][0]


def vectorizer_params(lang):
    """Return token_pattern and stop_words for the detected language."""
    if lang.startswith("ko"):
        return r"[가-힣]{2,}", None
    if lang.startswith("ja"):
        return r"[ぁ-んァ-ヶ一-龯]{2,}", None
    if lang.startswith("zh"):
        return r"[一-龯]{2,}", None
    if lang.startswith("en"):
        return r"(?u)\b[a-zA-Z]{3,}\b", "english"
    # Other Latin-script languages: no English stop words
    return r"(?u)\b[a-zA-Z]{3,}\b", None


def load_cfg():
    cfg = dict(DEFAULTS)
    try:
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            for k, v in json.load(f).items():
                if not k.startswith("_"):
                    cfg[k] = v
    except FileNotFoundError:
        pass
    return cfg


def main():
    try:
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.decomposition import LatentDirichletAllocation
        import numpy as np
    except ImportError:
        print("FAIL · scikit-learn 미설치. pip install scikit-learn", file=sys.stderr)
        sys.exit(2)

    cfg         = load_cfg()
    in_path     = os.path.join(DATA_DIR, cfg["INPUT_FILENAME"])
    out_md      = os.path.join(REPORTS_DIR, cfg["OUTPUT_FILENAME"])
    out_csv     = os.path.join(DATA_DIR, cfg["OUTPUT_CSV"])
    text_col    = str(cfg["TEXT_COL"])
    n_topics    = int(cfg["N_TOPICS"])
    n_top_words = int(cfg["N_TOP_WORDS"])
    max_feat    = int(cfg["MAX_FEATURES"])
    max_iter    = int(cfg["MAX_ITER"])
    random_state= int(cfg.get("RANDOM_STATE", 42))

    if not os.path.exists(in_path):
        print(f"FAIL · 입력 파일 없음: {in_path}", file=sys.stderr)
        sys.exit(2)

    with open(in_path, "r", encoding="utf-8", newline="") as f:
        reader    = csv.DictReader(f)
        rows      = list(reader)
        fieldnames= list(reader.fieldnames or [])

    if text_col not in fieldnames:
        print(f"FAIL · 컬럼 없음: '{text_col}'  (사용 가능: {fieldnames})", file=sys.stderr)
        sys.exit(2)

    texts = [str(r.get(text_col, "") or "") for r in rows]
    texts = [t if t.strip() else "empty" for t in texts]

    lang         = detect_lang(texts)
    tok_pattern, stop_words = vectorizer_params(lang)
    print(f"언어 감지: {lang}  →  token_pattern={tok_pattern!r}", flush=True)
    print(f"CountVectorizer 학습 중... (max_features={max_feat})", flush=True)
    vec = CountVectorizer(max_features=max_feat, stop_words=stop_words,
                          token_pattern=tok_pattern)
    dtm = vec.fit_transform(texts)
    feature_names = vec.get_feature_names_out()

    if dtm.shape[1] == 0:
        print(f"FAIL · 어휘가 0개입니다. 감지 언어: {lang}", file=sys.stderr)
        print(f"     · token_pattern='{tok_pattern}' 으로 매칭되는 단어가 없습니다.", file=sys.stderr)
        sys.exit(2)

    print(f"LDA 학습 중... (n_topics={n_topics}, max_iter={max_iter})", flush=True)
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        max_iter=max_iter,
        random_state=random_state,
        learning_method="batch",
    )
    doc_topic = lda.fit_transform(dtm)  # (n_docs, n_topics)

    # 주제별 상위 단어
    topic_top_words = []
    for topic_vec in lda.components_:
        top_idx  = topic_vec.argsort()[::-1][:n_top_words]
        words    = [feature_names[i] for i in top_idx]
        weights  = [topic_vec[i] for i in top_idx]
        topic_top_words.append(list(zip(words, weights)))

    # 문서별 dominant topic
    dominant_topics = doc_topic.argmax(axis=1).tolist()
    topic_probs     = doc_topic.max(axis=1).tolist()

    # 주제별 문서 수
    from collections import Counter
    topic_doc_count = Counter(dominant_topics)

    # 결과 CSV
    os.makedirs(DATA_DIR, exist_ok=True)
    base_fields = [f for f in fieldnames if f not in ("dominant_topic", "topic_prob")]
    out_fields = base_fields + ["dominant_topic", "topic_prob"]
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        for row, dt, tp in zip(rows, dominant_topics, topic_probs):
            clean = {k: v for k, v in row.items() if k is not None}
            writer.writerow({**clean, "dominant_topic": dt, "topic_prob": f"{tp:.4f}"})

    # 마크다운 리포트
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(f"# 💬 주제 모델링 리포트 — {cfg['INPUT_FILENAME']}\n\n")
        f.write(f"- **입력**: `{in_path}`\n")
        f.write(f"- **문서 수**: {len(rows):,}\n")
        f.write(f"- **텍스트 컬럼**: `{text_col}`\n")
        f.write(f"- **감지 언어**: `{lang}` (token_pattern: `{tok_pattern}`)\n")
        f.write(f"- **추출 주제 수**: {n_topics}\n")
        f.write(f"- **어휘 크기**: {dtm.shape[1]:,} 단어\n\n")

        f.write("## 1. 주제별 상위 단어\n\n")
        for ti, words_weights in enumerate(topic_top_words):
            doc_cnt = topic_doc_count.get(ti, 0)
            f.write(f"### 주제 {ti} ({doc_cnt}건)\n\n")
            f.write("| 순위 | 단어 | 가중치 |\n|---:|---|---:|\n")
            for rank, (word, weight) in enumerate(words_weights, 1):
                f.write(f"| {rank} | `{word}` | {weight:.2f} |\n")
            f.write("\n")

        f.write("## 2. 문서별 주제 배정 요약\n\n")
        f.write("| 주제 | 문서 수 | 비율 |\n|---|---:|---:|\n")
        total = len(rows)
        for ti in range(n_topics):
            cnt = topic_doc_count.get(ti, 0)
            f.write(f"| 주제 {ti} | {cnt:,} | {cnt/total*100:.1f}% |\n")
        f.write("\n")

        f.write("## 3. 한계 / 주의\n\n")
        f.write("- 언어를 자동 감지해 token_pattern을 선택합니다: 한국어·일본어·중국어·영어 지원.\n")
        f.write("- 한국어는 어절(띄어쓰기) 단위로 분리되므로 형태소 분석기(konlpy 등)보다 정밀도가 낮을 수 있습니다.\n")
        f.write("- N_TOPICS 값에 따라 결과가 크게 달라집니다. 여러 값을 시도해 보세요.\n")
        f.write("- 주제 이름은 자동 부여되지 않습니다. 상위 단어를 보고 직접 해석하세요.\n")
        f.write("- 결과 CSV의 `dominant_topic`을 `eda_runner`나 `sentiment_analyzer` 결과와 결합해 '주제별 감성 분포' 분석 가능.\n")

    print("=" * 60)
    print(f"OK · topic_modeler")
    print(f"  input:    {in_path}")
    print(f"  docs:     {len(rows):,}")
    print(f"  vocab:    {dtm.shape[1]:,} words")
    print(f"  topics:   {n_topics}")
    for ti in range(n_topics):
        top3 = ", ".join(w for w, _ in topic_top_words[ti][:3])
        print(f"    topic {ti}: {top3} ...")
    print(f"  report:   {out_md}")
    print(f"  csv:      {out_csv}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except SystemExit:
        raise
    except Exception as e:
        print(f"FAIL · {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
