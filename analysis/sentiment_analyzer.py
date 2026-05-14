#!/usr/bin/env python3
"""sentiment_analyzer — 다국어 CSV → 감성 분석(langdetect + xlm-roberta) → 마크다운 리포트 + 결과 CSV.

읽기:  sentiment_analyzer.json
입력:  ../../../data/<INPUT_FILENAME>
출력:  ../../../reports/<OUTPUT_FILENAME>  (리포트)
       ../../../data/<OUTPUT_CSV>          (행별 결과)

첫 실행 시 cardiffnlp/twitter-xlm-roberta-base-sentiment 모델 ~280MB 자동 다운로드.
"""
import json, os, sys, csv
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CFG_PATH  = os.path.join(HERE, "sentiment_analyzer.json")
DATA_DIR  = os.path.normpath(os.path.join(HERE, "..", "..", "..", "data"))
REPORTS_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "reports"))

DEFAULTS = {
    "INPUT_FILENAME":  "data.csv",
    "TEXT_COL":        "text",
    "OUTPUT_FILENAME": "data_sentiment.md",
    "OUTPUT_CSV":      "data_sentiment.csv",
    "BATCH_SIZE":      32,
    "MAX_ROWS":        0,
}

MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
LABELS = ["negative", "neutral", "positive"]


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


def detect_lang(text):
    try:
        from langdetect import detect
        return detect(str(text))
    except Exception:
        return "unknown"


def load_pipeline():
    try:
        from transformers import pipeline
    except ImportError:
        print("FAIL · transformers가 설치되지 않았습니다.", file=sys.stderr)
        print("     · pip install transformers torch 를 실행하세요.", file=sys.stderr)
        sys.exit(2)
    print(f"모델 로드 중: {MODEL_NAME}  (첫 실행은 ~280MB 다운로드)", flush=True)
    return pipeline(
        "sentiment-analysis",
        model=MODEL_NAME,
        tokenizer=MODEL_NAME,
        top_k=1,
        truncation=True,
        max_length=512,
    )


def run_batch(pipe, texts):
    results = pipe(texts)
    out = []
    for r in results:
        top = r[0] if isinstance(r, list) else r
        label = top["label"].lower()
        score = round(top["score"], 4)
        out.append((label, score))
    return out


def fmt_pct(n, total):
    return f"{n:,} ({n/total*100:.1f}%)" if total else "0"


def main():
    cfg = load_cfg()
    in_path  = os.path.join(DATA_DIR, cfg["INPUT_FILENAME"])
    out_md   = os.path.join(REPORTS_DIR, cfg["OUTPUT_FILENAME"])
    out_csv  = os.path.join(DATA_DIR, cfg["OUTPUT_CSV"])
    text_col = cfg["TEXT_COL"]
    batch_sz = int(cfg["BATCH_SIZE"])
    max_rows = int(cfg["MAX_ROWS"])

    if not os.path.exists(in_path):
        print(f"FAIL · 입력 파일 없음: {in_path}", file=sys.stderr)
        sys.exit(2)

    with open(in_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if not rows:
        print(f"FAIL · CSV가 비어 있습니다: {in_path}", file=sys.stderr)
        sys.exit(2)

    if text_col not in fieldnames:
        print(f"FAIL · 컬럼 '{text_col}' 이 CSV에 없습니다.", file=sys.stderr)
        print(f"     · 사용 가능한 컬럼: {fieldnames}", file=sys.stderr)
        sys.exit(2)

    if max_rows > 0:
        rows = rows[:max_rows]

    texts = [str(r.get(text_col, "") or "") for r in rows]

    print(f"언어 탐지 중... ({len(rows):,}행)", flush=True)
    langs = [detect_lang(t) for t in texts]

    pipe = load_pipeline()

    print(f"감성 분석 중... (배치 크기={batch_sz})", flush=True)
    sentiments, scores = [], []
    for i in range(0, len(texts), batch_sz):
        batch = texts[i : i + batch_sz]
        batch = [t if t.strip() else "." for t in batch]
        for label, score in run_batch(pipe, batch):
            sentiments.append(label)
            scores.append(score)
        done = min(i + batch_sz, len(texts))
        print(f"  {done:,}/{len(texts):,}", flush=True)

    # 결과 CSV (이미 lang/sentiment/score 컬럼이 있으면 덮어쓰기 방지를 위해 제외 후 추가)
    os.makedirs(DATA_DIR, exist_ok=True)
    base_fields = [f for f in fieldnames if f not in ("lang", "sentiment", "score")]
    out_fields = base_fields + ["lang", "sentiment", "score"]
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        for row, lang, sent, sc in zip(rows, langs, sentiments, scores):
            clean = {k: v for k, v in row.items() if k is not None and k in base_fields}
            writer.writerow({**clean, "lang": lang, "sentiment": sent, "score": sc})

    # 통계 계산
    total = len(rows)
    sent_count  = Counter(sentiments)
    lang_count  = Counter(langs)
    lang_sent   = defaultdict(Counter)
    for lang, sent in zip(langs, sentiments):
        lang_sent[lang][sent] += 1

    # 고신뢰도 예시 (positive / negative 각 상위 3건)
    examples = {"positive": [], "negative": []}
    for i, (sent, sc) in enumerate(zip(sentiments, scores)):
        if sent in examples:
            examples[sent].append((sc, texts[i][:120], langs[i]))
    for k in examples:
        examples[k] = sorted(examples[k], reverse=True)[:3]

    # 마크다운 리포트
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(f"# 🌐 다국어 감성 분석 리포트 — {cfg['INPUT_FILENAME']}\n\n")
        f.write(f"- **입력**: `{in_path}`\n")
        f.write(f"- **분석 행 수**: {total:,}\n")
        f.write(f"- **텍스트 컬럼**: `{text_col}`\n")
        f.write(f"- **모델**: `{MODEL_NAME}`\n\n")

        f.write("## 1. 전체 감성 분포\n\n")
        f.write("| 감성 | 건수 | 비율 |\n|---|---:|---:|\n")
        for label in LABELS:
            cnt = sent_count.get(label, 0)
            f.write(f"| {label} | {cnt:,} | {cnt/total*100:.1f}% |\n")
        f.write("\n")

        f.write("## 2. 언어 분포\n\n")
        f.write("| 언어 코드 | 건수 | 비율 |\n|---|---:|---:|\n")
        for lang, cnt in lang_count.most_common(20):
            f.write(f"| `{lang}` | {cnt:,} | {cnt/total*100:.1f}% |\n")
        f.write("\n")

        f.write("## 3. 언어별 감성 교차표\n\n")
        f.write("| 언어 | positive | neutral | negative | 계 |\n|---|---:|---:|---:|---:|\n")
        for lang, cnt in lang_count.most_common(15):
            sc = lang_sent[lang]
            pos = sc.get("positive", 0)
            neu = sc.get("neutral", 0)
            neg = sc.get("negative", 0)
            f.write(f"| `{lang}` | {pos} | {neu} | {neg} | {cnt} |\n")
        f.write("\n")

        f.write("## 4. 고신뢰도 예시\n\n")
        for sentiment in ("positive", "negative"):
            f.write(f"### {sentiment.capitalize()} (신뢰도 상위 3건)\n\n")
            ex = examples[sentiment]
            if ex:
                for sc, text, lang in ex:
                    f.write(f"- `[{lang}]` score={sc:.3f}  \n  > {text}\n")
            else:
                f.write("_해당 감성 결과 없음_\n")
            f.write("\n")

        f.write("## 5. 한계 / 주의\n\n")
        f.write("- 본 리포트는 자동 감성 분류 결과입니다. 인과 단정 금지 — 상관/관찰만 보고.\n")
        f.write("- `langdetect`는 짧은 텍스트(< 10자)에서 오탐 가능 (`unknown` 표기).\n")
        f.write("- 모델은 소셜 미디어 텍스트에 파인튜닝되어 정제된 문어체에서는 정확도가 낮을 수 있음.\n")
        f.write("- 결과 CSV에 `lang`, `sentiment`, `score` 컬럼이 추가되어 추가 분석 가능.\n")

    print("=" * 60)
    print(f"OK · sentiment_analyzer")
    print(f"  input:   {in_path}")
    print(f"  rows:    {total:,}")
    print(f"  report:  {out_md}")
    print(f"  csv:     {out_csv}")
    dist = "  |  ".join(f"{l}:{sent_count.get(l,0)}" for l in LABELS)
    print(f"  dist:    {dist}")
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
