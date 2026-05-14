#!/usr/bin/env python3
"""weighted_score_runner — 항목×지표 점수 CSV + 가중치 → 가중 합산 순위 리포트 + 바 차트 PNG.

읽기:  weighted_score_runner.json
입력:  ../../../data/<INPUT_FILENAME>
출력:  ../../../reports/<OUTPUT_FILENAME>  (순위 리포트)
       ../../../reports/<OUTPUT_PLOT>      (항목별 최종 점수 바 차트)
"""
import csv, json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

HERE        = os.path.dirname(os.path.abspath(__file__))
CFG_PATH    = os.path.join(HERE, "weighted_score_runner.json")
DATA_DIR    = os.path.normpath(os.path.join(HERE, "..", "..", "..", "data"))
REPORTS_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "reports"))

DEFAULTS = {
    "INPUT_FILENAME":   "genre_scores.csv",
    "ITEM_COL":         "genre",
    "SCORE_COLS":       ["input_precision", "marketing_conversion", "hardware_friction", "core_loop"],
    "WEIGHTS":          {},
    "HIGHER_IS_BETTER": {},
    "NORMALIZE":        True,
    "OUTPUT_FILENAME":  "genre_scores_weighted.md",
    "OUTPUT_PLOT":      "genre_scores_weighted.png",
}


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


def to_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def minmax(values):
    valid = [v for v in values if v is not None]
    if not valid:
        return [0.5 if v is not None else None for v in values]
    mn, mx = min(valid), max(valid)
    if mx == mn:
        return [0.5 if v is not None else None for v in values]
    return [(v - mn) / (mx - mn) if v is not None else None for v in values]


def main():
    cfg        = load_cfg()
    in_path    = os.path.join(DATA_DIR, cfg["INPUT_FILENAME"])
    out_md     = os.path.join(REPORTS_DIR, cfg["OUTPUT_FILENAME"])
    out_plot   = os.path.join(REPORTS_DIR, cfg["OUTPUT_PLOT"])
    item_col   = str(cfg["ITEM_COL"])
    score_cols = list(cfg["SCORE_COLS"])
    weights    = {str(k): float(v) for k, v in dict(cfg["WEIGHTS"]).items()}
    hib        = {str(k): bool(v) for k, v in dict(cfg["HIGHER_IS_BETTER"]).items()}
    normalize  = bool(cfg["NORMALIZE"])

    if not os.path.exists(in_path):
        print(f"FAIL · 입력 파일 없음: {in_path}", file=sys.stderr)
        sys.exit(2)

    with open(in_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows   = list(reader)
        header = list(reader.fieldnames or [])

    if item_col not in header:
        print(f"FAIL · ITEM_COL '{item_col}' 없음. 사용 가능: {header}", file=sys.stderr)
        sys.exit(2)

    missing = [c for c in score_cols if c not in header]
    if missing:
        print(f"FAIL · SCORE_COLS 중 없는 컬럼: {missing}", file=sys.stderr)
        sys.exit(2)

    if not rows:
        print("FAIL · 데이터 행이 없습니다.", file=sys.stderr)
        sys.exit(2)

    items     = [r.get(item_col, f"item_{i}") for i, r in enumerate(rows)]
    raw       = {col: [to_float(r.get(col, "")) for r in rows] for col in score_cols}

    # 정규화 (min-max)
    if normalize:
        normed = {col: minmax(raw[col]) for col in score_cols}
    else:
        normed = {col: list(raw[col]) for col in score_cols}

    # HIGHER_IS_BETTER=False → 반전 (정규화 후)
    adjusted = {}
    for col in score_cols:
        col_hib = hib.get(col, True)
        adjusted[col] = [
            (1.0 - v) if (v is not None and not col_hib) else v
            for v in normed[col]
        ]

    # 유효 가중치 (미지정 컬럼 = 1.0)
    w       = {col: weights.get(col, 1.0) for col in score_cols}
    total_w = sum(w.values())

    # 가중 합산 점수
    final = []
    for i in range(len(rows)):
        wsum  = sum(adjusted[col][i] * w[col] for col in score_cols if adjusted[col][i] is not None)
        uw    = sum(w[col] for col in score_cols if adjusted[col][i] is not None)
        final.append((wsum / uw) if uw > 0 else 0.0)

    # 순위 정렬
    ranked_idx = sorted(range(len(rows)), key=lambda i: -final[i])

    # 바 차트
    os.makedirs(REPORTS_DIR, exist_ok=True)
    r_items  = [items[i] for i in ranked_idx]
    r_scores = [final[i] for i in ranked_idx]
    n        = len(r_items)
    colors   = [cm.RdYlGn(0.1 + 0.8 * (n - 1 - rank) / max(n - 1, 1)) for rank in range(n)]

    fig, ax = plt.subplots(figsize=(9, max(4, n * 0.55)))
    bars = ax.barh(range(n), r_scores, color=list(reversed(colors)))
    ax.set_yticks(range(n))
    ax.set_yticklabels(list(reversed(r_items)), fontsize=10)
    ax.set_xlabel("Weighted Score (0 ~ 1)")
    ax.set_title("Weighted Score Ranking")
    ax.set_xlim(0, 1.05)
    for j, (bar, sc) in enumerate(zip(bars, list(reversed(r_scores)))):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{sc:.3f}", va="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(out_plot, dpi=120)
    plt.close()

    # 마크다운 리포트
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(f"# 가중 점수 순위 리포트 — {cfg['INPUT_FILENAME']}\n\n")
        f.write(f"- **입력**: `{in_path}`\n")
        f.write(f"- **항목 컬럼**: `{item_col}`\n")
        f.write(f"- **정규화**: {'min-max (0~1)' if normalize else '원본 값 그대로'}\n\n")

        f.write("## 1. 지표 설정\n\n")
        f.write("| 지표 | 가중치 | 높을수록 유리 |\n|---|---:|:---:|\n")
        for col in score_cols:
            hib_mark = "✅" if hib.get(col, True) else "❌ (반전 적용)"
            f.write(f"| `{col}` | {w[col]:.2f} | {hib_mark} |\n")
        f.write(f"\n_총 가중치 합: {total_w:.2f}_\n\n")

        f.write("## 2. 순위 결과\n\n")
        header_cols = " | ".join(f"`{c}`" for c in score_cols)
        sep_cols    = " | ".join("---:" for _ in score_cols)
        f.write(f"| 순위 | {item_col} | {header_cols} | **최종 점수** |\n")
        f.write(f"|---:|---|{sep_cols}|---:|\n")
        for rank, idx in enumerate(ranked_idx, 1):
            raw_vals = " | ".join(
                f"{raw[col][idx]:.2f}" if raw[col][idx] is not None else "—"
                for col in score_cols
            )
            f.write(f"| {rank} | **{items[idx]}** | {raw_vals} | **{final[idx]:.4f}** |\n")
        f.write(f"\n![가중 점수 바 차트]({cfg['OUTPUT_PLOT']})\n\n")

        f.write("## 3. 점수 계산 방식\n\n")
        f.write("1. 각 지표를 min-max 정규화 → [0, 1]\n" if normalize else
                "1. 정규화 생략 (원본 값 그대로 사용)\n")
        f.write("2. `HIGHER_IS_BETTER: false` 지표는 `1 − 정규화값` 으로 반전\n")
        f.write("3. `최종 점수 = Σ(조정값 × 가중치) / Σ가중치`\n\n")

        f.write("## 4. 주의\n\n")
        f.write("- 점수는 입력된 항목 간 상대 비교이므로 항목이 바뀌면 순위도 바뀝니다.\n")
        f.write("- 가중치가 모두 동일하면 단순 평균 순위와 같습니다.\n")
        f.write("- 결측값이 있는 지표는 해당 항목 계산에서 제외되고 나머지 지표로만 산출됩니다.\n")

    print("=" * 60)
    print(f"OK · weighted_score_runner")
    print(f"  input:   {in_path}")
    print(f"  items:   {len(rows)}")
    print(f"  top:     {items[ranked_idx[0]]}  ({final[ranked_idx[0]]:.4f})")
    print(f"  report:  {out_md}")
    print(f"  plot:    {out_plot}")
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
