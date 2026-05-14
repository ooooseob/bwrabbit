#!/usr/bin/env python3
"""survey_analyzer — Likert 설문 CSV → 기술통계 + Cronbach α + 피로도 곡선 + 히스토그램 PNG.

읽기:  survey_analyzer.json
입력:  ../../../data/<INPUT_FILENAME>
출력:  ../../../reports/<OUTPUT_FILENAME>  (마크다운 리포트)
       ../../../reports/<OUTPUT_PLOT>      (문항별 히스토그램 + 피로도 곡선 PNG)
"""
import csv, json, math, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE        = os.path.dirname(os.path.abspath(__file__))
CFG_PATH    = os.path.join(HERE, "survey_analyzer.json")
DATA_DIR    = os.path.normpath(os.path.join(HERE, "..", "..", "..", "data"))
REPORTS_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "reports"))

DEFAULTS = {
    "INPUT_FILENAME":  "fatigue_survey.csv",
    "QUESTION_COLS":   ["q1", "q2", "q3", "q4", "q5"],
    "ITEM_COL":        "",
    "TIME_COL":        "",
    "SCALE_MAX":       5,
    "OUTPUT_FILENAME": "fatigue_survey_report.md",
    "OUTPUT_PLOT":     "fatigue_survey_plot.png",
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


def variance(values, ddof=1):
    n = len(values)
    if n <= ddof:
        return 0.0
    mean = sum(values) / n
    return sum((v - mean) ** 2 for v in values) / (n - ddof)


def cronbach_alpha(matrix):
    """matrix: list of lists (응답자 × 문항). 유효 값만 포함된 행 기준."""
    k = len(matrix[0]) if matrix else 0
    if k < 2:
        return None
    item_vars  = []
    totals     = []
    for row in matrix:
        totals.append(sum(row))
    for j in range(k):
        col_vals = [matrix[i][j] for i in range(len(matrix))]
        item_vars.append(variance(col_vals))
    total_var = variance(totals)
    if total_var == 0:
        return None
    alpha = (k / (k - 1)) * (1 - sum(item_vars) / total_var)
    return alpha


def interpret_alpha(a):
    if a is None:
        return "계산 불가 (총점 분산 0)"
    if a >= 0.9:  return f"{a:.3f} — Excellent (α ≥ 0.9)"
    if a >= 0.8:  return f"{a:.3f} — Good (α ≥ 0.8)"
    if a >= 0.7:  return f"{a:.3f} — Acceptable (α ≥ 0.7)"
    if a >= 0.6:  return f"{a:.3f} — Questionable (α ≥ 0.6)"
    return f"{a:.3f} — Poor (α < 0.6) — 문항 재검토 필요"


def desc(values):
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": None, "std": None, "min": None, "max": None, "median": None}
    mean   = sum(values) / n
    std    = math.sqrt(variance(values))
    sorted_v = sorted(values)
    mid    = n // 2
    median = sorted_v[mid] if n % 2 else (sorted_v[mid - 1] + sorted_v[mid]) / 2
    return {"n": n, "mean": mean, "std": std, "min": min(values), "max": max(values), "median": median}


def fmt(v, d=2):
    return f"{v:.{d}f}" if v is not None else "—"


def main():
    cfg         = load_cfg()
    in_path     = os.path.join(DATA_DIR, cfg["INPUT_FILENAME"])
    out_md      = os.path.join(REPORTS_DIR, cfg["OUTPUT_FILENAME"])
    out_plot    = os.path.join(REPORTS_DIR, cfg["OUTPUT_PLOT"])
    q_cols      = list(cfg["QUESTION_COLS"])
    item_col    = str(cfg["ITEM_COL"]).strip()
    time_col    = str(cfg["TIME_COL"]).strip()
    scale_max   = int(cfg["SCALE_MAX"])

    if not q_cols:
        print("FAIL · QUESTION_COLS가 비어 있습니다.", file=sys.stderr)
        sys.exit(2)

    if not os.path.exists(in_path):
        print(f"FAIL · 입력 파일 없음: {in_path}", file=sys.stderr)
        sys.exit(2)

    with open(in_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows   = list(reader)
        header = list(reader.fieldnames or [])

    missing = [c for c in q_cols if c not in header]
    if missing:
        print(f"FAIL · QUESTION_COLS 중 없는 컬럼: {missing}", file=sys.stderr)
        sys.exit(2)

    if time_col and time_col not in header:
        print(f"FAIL · TIME_COL '{time_col}' 없음. 사용 가능: {header}", file=sys.stderr)
        sys.exit(2)

    if not rows:
        print("FAIL · 데이터 행이 없습니다.", file=sys.stderr)
        sys.exit(2)

    # 문항별 값 파싱
    col_vals = {col: [] for col in q_cols}
    for r in rows:
        for col in q_cols:
            v = to_float(r.get(col, ""))
            if v is not None:
                col_vals[col].append(v)

    # Cronbach alpha — 완전한 응답만 사용
    valid_matrix = []
    for r in rows:
        row_vals = [to_float(r.get(col, "")) for col in q_cols]
        if None not in row_vals:
            valid_matrix.append(row_vals)
    alpha = cronbach_alpha(valid_matrix) if len(valid_matrix) >= 2 else None

    # 총점 (응답자별)
    total_scores = []
    for r in rows:
        row_vals = [to_float(r.get(col, "")) for col in q_cols]
        valid    = [v for v in row_vals if v is not None]
        if valid:
            total_scores.append(sum(valid))

    # 피로도 곡선 (TIME_COL 있을 때)
    time_data = {}
    if time_col:
        for r in rows:
            t = to_float(r.get(time_col, ""))
            if t is None:
                continue
            row_vals = [to_float(r.get(col, "")) for col in q_cols]
            valid    = [v for v in row_vals if v is not None]
            if valid:
                mean_score = sum(valid) / len(valid)
                time_data.setdefault(t, []).append(mean_score)
        time_data = {t: sum(vs) / len(vs) for t, vs in sorted(time_data.items())}

    # 차트 생성
    os.makedirs(REPORTS_DIR, exist_ok=True)
    has_fatigue = bool(time_data)
    n_q         = len(q_cols)
    n_cols_plot = min(3, n_q)
    n_rows_plot = math.ceil(n_q / n_cols_plot) + (1 if has_fatigue else 0)
    fig_h       = max(4, n_rows_plot * 3)

    fig = plt.figure(figsize=(5 * n_cols_plot, fig_h))

    # 문항별 히스토그램
    bins = [i - 0.5 for i in range(1, scale_max + 2)]
    for qi, col in enumerate(q_cols):
        ax = fig.add_subplot(n_rows_plot, n_cols_plot, qi + 1)
        vals = col_vals[col]
        ax.hist(vals, bins=bins, color="#3498db", edgecolor="white", rwidth=0.8)
        ax.set_title(col, fontsize=10)
        ax.set_xlabel(f"점수 (1~{scale_max})")
        ax.set_ylabel("응답 수")
        ax.set_xticks(range(1, scale_max + 1))
        ax.set_xlim(0.5, scale_max + 0.5)
        d = desc(vals)
        ax.axvline(d["mean"], color="#e74c3c", linestyle="--", linewidth=1.5,
                   label=f"평균 {d['mean']:.2f}")
        ax.legend(fontsize=8)

    # 피로도 곡선
    if has_fatigue:
        ax_fat = fig.add_subplot(n_rows_plot, 1, n_rows_plot)
        times  = list(time_data.keys())
        scores = list(time_data.values())
        ax_fat.plot(times, scores, marker="o", color="#e74c3c", linewidth=2)
        ax_fat.fill_between(times, scores, alpha=0.15, color="#e74c3c")
        ax_fat.set_xlabel(f"{time_col} (분)")
        ax_fat.set_ylabel("평균 점수")
        ax_fat.set_title("피로도 곡선 — 시간에 따른 평균 점수 변화")
        ax_fat.set_ylim(0, scale_max + 0.5)
        ax_fat.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(out_plot, dpi=120, bbox_inches="tight")
    plt.close()

    # 마크다운 리포트
    total_d = desc(total_scores)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(f"# 설문 분석 리포트 — {cfg['INPUT_FILENAME']}\n\n")
        f.write(f"- **입력**: `{in_path}`\n")
        f.write(f"- **총 응답자 수**: {len(rows):,}\n")
        f.write(f"- **분석 문항 수**: {len(q_cols)}\n")
        f.write(f"- **척도 최댓값**: {scale_max}\n")
        if time_col:
            f.write(f"- **시간 컬럼**: `{time_col}` (피로도 곡선 포함)\n")
        f.write("\n")

        f.write("## 1. 신뢰도 — Cronbach α\n\n")
        f.write(f"| 항목 | 값 |\n|---|---|\n")
        f.write(f"| 완전 응답자 수 (α 계산 기준) | {len(valid_matrix):,} |\n")
        f.write(f"| **Cronbach α** | **{interpret_alpha(alpha)}** |\n\n")
        f.write("_α ≥ 0.7이면 설문 도구 신뢰성 확보. 낮으면 문항 재검토._\n\n")

        f.write("## 2. 문항별 기술통계\n\n")
        f.write("| 문항 | n | 평균 | 표준편차 | 중앙값 | 최솟값 | 최댓값 |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|\n")
        for col in q_cols:
            d = desc(col_vals[col])
            f.write(f"| `{col}` | {d['n']:,} | {fmt(d['mean'])} | {fmt(d['std'])} | "
                    f"{fmt(d['median'])} | {fmt(d['min'], 0)} | {fmt(d['max'], 0)} |\n")
        f.write("\n")

        f.write("## 3. 총점 요약\n\n")
        f.write("| 항목 | 값 |\n|---|---:|\n")
        f.write(f"| 총점 평균 | {fmt(total_d['mean'])} |\n")
        f.write(f"| 총점 표준편차 | {fmt(total_d['std'])} |\n")
        f.write(f"| 총점 최솟값 | {fmt(total_d['min'])} |\n")
        f.write(f"| 총점 최댓값 | {fmt(total_d['max'])} |\n")
        f.write(f"| 총점 최대 가능 | {len(q_cols) * scale_max} |\n\n")

        if has_fatigue:
            f.write("## 4. 피로도 곡선 요약\n\n")
            f.write(f"| {time_col} | 평균 점수 |\n|---:|---:|\n")
            for t, s in time_data.items():
                f.write(f"| {t:.0f} | {s:.3f} |\n")
            times_list  = list(time_data.keys())
            scores_list = list(time_data.values())
            if len(scores_list) >= 2:
                drop = scores_list[-1] - scores_list[0]
                f.write(f"\n_시작 → 끝 점수 변화: {drop:+.3f} "
                        f"({'하락 (피로도 증가 의심)' if drop < 0 else '유지/상승'})_\n\n")

        f.write(f"![설문 차트]({cfg['OUTPUT_PLOT']})\n\n")

        f.write("## 5. 주의\n\n")
        f.write("- Cronbach α는 **문항 간 내적 일관성**이며 타당도(validity)와는 다릅니다.\n")
        f.write("- 피로도 곡선은 `TIME_COL`이 지정된 경우에만 생성됩니다.\n")
        f.write("- Likert 척도 값은 1 이상이어야 합니다. 0은 결측으로 처리됩니다.\n")
        f.write("- 문항 수가 2개 미만이면 α를 계산할 수 없습니다.\n")

    print("=" * 60)
    print(f"OK · survey_analyzer")
    print(f"  input:       {in_path}")
    print(f"  respondents: {len(rows):,}")
    print(f"  questions:   {q_cols}")
    print(f"  alpha:       {interpret_alpha(alpha)}")
    print(f"  report:      {out_md}")
    print(f"  plot:        {out_plot}")
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
