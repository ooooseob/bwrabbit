#!/usr/bin/env python3
"""radar_chart_runner — 항목×지표 점수 CSV → 레이더(스파이더) 차트 PNG + 지표별 점수 비교 리포트.

읽기:  radar_chart_runner.json
입력:  ../../../data/<INPUT_FILENAME>
출력:  ../../../reports/<OUTPUT_FILENAME>  (마크다운 리포트)
       ../../../reports/<OUTPUT_PLOT>      (레이더 차트 PNG)
"""
import csv, json, math, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE        = os.path.dirname(os.path.abspath(__file__))
CFG_PATH    = os.path.join(HERE, "radar_chart_runner.json")
DATA_DIR    = os.path.normpath(os.path.join(HERE, "..", "..", "..", "data"))
REPORTS_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "reports"))

DEFAULTS = {
    "INPUT_FILENAME":   "genre_scores.csv",
    "ITEM_COL":         "genre",
    "SCORE_COLS":       ["input_precision", "marketing_conversion", "hardware_friction", "core_loop"],
    "HIGHER_IS_BETTER": {},
    "NORMALIZE":        True,
    "MAX_ITEMS":        8,
    "OUTPUT_FILENAME":  "genre_scores_radar.md",
    "OUTPUT_PLOT":      "genre_scores_radar.png",
}

COLORS = [
    "#e74c3c", "#3498db", "#2ecc71", "#f39c12",
    "#9b59b6", "#1abc9c", "#e67e22", "#34495e",
]


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


def draw_radar(ax, angles, values, color, label, alpha=0.25):
    vals = values + [values[0]]
    angs = angles + [angles[0]]
    ax.plot(angs, vals, color=color, linewidth=2, label=label)
    ax.fill(angs, vals, color=color, alpha=alpha)


def main():
    cfg        = load_cfg()
    in_path    = os.path.join(DATA_DIR, cfg["INPUT_FILENAME"])
    out_md     = os.path.join(REPORTS_DIR, cfg["OUTPUT_FILENAME"])
    out_plot   = os.path.join(REPORTS_DIR, cfg["OUTPUT_PLOT"])
    item_col   = str(cfg["ITEM_COL"])
    score_cols = list(cfg["SCORE_COLS"])
    hib        = {str(k): bool(v) for k, v in dict(cfg["HIGHER_IS_BETTER"]).items()}
    normalize  = bool(cfg["NORMALIZE"])
    max_items  = int(cfg["MAX_ITEMS"])

    if len(score_cols) < 3:
        print("FAIL · SCORE_COLS는 레이더 차트에 3개 이상이어야 합니다.", file=sys.stderr)
        sys.exit(2)

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

    # 항목 수 제한
    if len(rows) > max_items:
        print(f"  MAX_ITEMS={max_items} 초과 → 앞 {max_items}개 항목만 사용", flush=True)
        rows = rows[:max_items]

    items     = [r.get(item_col, f"item_{i}") for i, r in enumerate(rows)]
    raw       = {col: [to_float(r.get(col, "")) for r in rows] for col in score_cols}

    # 정규화
    if normalize:
        normed = {col: minmax(raw[col]) for col in score_cols}
    else:
        normed = {col: list(raw[col]) for col in score_cols}

    # HIGHER_IS_BETTER=False → 반전
    adjusted = {}
    for col in score_cols:
        col_hib = hib.get(col, True)
        adjusted[col] = [
            (1.0 - v) if (v is not None and not col_hib) else v
            for v in normed[col]
        ]

    # 결측값 → 0.0 처리 (차트 표시용)
    plot_vals = {
        col: [v if v is not None else 0.0 for v in adjusted[col]]
        for col in score_cols
    }

    # 각도 계산
    n_axes  = len(score_cols)
    angles  = [2 * math.pi * i / n_axes for i in range(n_axes)]
    labels  = [
        f"{col}\n({'↑' if hib.get(col, True) else '↓→↑반전'})"
        for col in score_cols
    ]

    # 레이더 차트
    os.makedirs(REPORTS_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})

    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids([math.degrees(a) for a in angles], labels, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=8)
    ax.grid(color="grey", linestyle="--", linewidth=0.5, alpha=0.7)

    for i, item in enumerate(items):
        color  = COLORS[i % len(COLORS)]
        values = [plot_vals[col][i] for col in score_cols]
        draw_radar(ax, angles, values, color, item)

    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=9)
    ax.set_title("Radar Chart — Genre Indicator Comparison", pad=20, fontsize=12)
    plt.tight_layout()
    plt.savefig(out_plot, dpi=120, bbox_inches="tight")
    plt.close()

    # 마크다운 리포트
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(f"# 레이더 차트 리포트 — {cfg['INPUT_FILENAME']}\n\n")
        f.write(f"- **입력**: `{in_path}`\n")
        f.write(f"- **항목 컬럼**: `{item_col}`\n")
        f.write(f"- **정규화**: {'min-max (0~1)' if normalize else '원본 값 그대로'}\n")
        f.write(f"- **표시 항목 수**: {len(items)}\n\n")

        f.write(f"![레이더 차트]({cfg['OUTPUT_PLOT']})\n\n")

        f.write("## 1. 지표 설정\n\n")
        f.write("| 지표 | 높을수록 유리 | 비고 |\n|---|:---:|---|\n")
        for col in score_cols:
            col_hib = hib.get(col, True)
            note = "" if col_hib else "차트에서 반전 표시됨 (낮을수록 바깥으로)"
            f.write(f"| `{col}` | {'✅' if col_hib else '❌'} | {note} |\n")
        f.write("\n")

        f.write("## 2. 항목별 점수 (정규화 후)\n\n")
        col_headers = " | ".join(f"`{c}`" for c in score_cols)
        col_seps    = " | ".join("---:" for _ in score_cols)
        f.write(f"| {item_col} | {col_headers} |\n|---|{col_seps}|\n")
        for i, item in enumerate(items):
            vals_str = " | ".join(
                f"{plot_vals[col][i]:.3f}" for col in score_cols
            )
            f.write(f"| **{item}** | {vals_str} |\n")
        f.write("\n")

        f.write("## 3. 주의\n\n")
        f.write("- 레이더 차트는 항목 간 **상대 비교**이므로 항목이 바뀌면 모양도 바뀝니다.\n")
        f.write("- `HIGHER_IS_BETTER: false` 지표는 반전 처리되어 '바깥=유리'로 통일됩니다.\n")
        f.write(f"- 항목이 {max_items}개 초과 시 앞 {max_items}개만 표시됩니다 (`MAX_ITEMS` 조정 가능).\n")
        f.write("- 3개 미만 지표로는 레이더 차트를 생성할 수 없습니다.\n")

    print("=" * 60)
    print(f"OK · radar_chart_runner")
    print(f"  input:   {in_path}")
    print(f"  items:   {items}")
    print(f"  axes:    {score_cols}")
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
