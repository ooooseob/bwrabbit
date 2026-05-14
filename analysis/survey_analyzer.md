# survey_analyzer

Likert 척도 설문 CSV → 기술통계 + Cronbach α + 피로도 곡선 + 문항별 히스토그램 PNG.

## 파라미터 (survey_analyzer.json)

| 파라미터 | 기본값 | 설명 |
|---|---|---|
| `INPUT_FILENAME` | `fatigue_survey.csv` | `_company/data/` 기준 입력 CSV |
| `QUESTION_COLS` | `["q1","q2","q3","q4","q5"]` | Likert 점수가 있는 문항 컬럼 목록 |
| `ITEM_COL` | `""` | 응답자 식별 컬럼. 빈 문자열이면 사용 안 함 |
| `TIME_COL` | `""` | 시간(분) 컬럼명. 지정 시 피로도 곡선 생성 |
| `SCALE_MAX` | `5` | Likert 척도 최댓값 (보통 5 또는 7) |
| `OUTPUT_FILENAME` | `fatigue_survey_report.md` | 리포트 파일명 |
| `OUTPUT_PLOT` | `fatigue_survey_plot.png` | 차트 PNG 파일명 |

## 출력

- `_company/reports/<OUTPUT_FILENAME>` — Cronbach α + 문항별 기술통계 + 총점 요약 + 피로도 곡선 요약
- `_company/reports/<OUTPUT_PLOT>` — 문항별 히스토그램 (평균선 포함) + 피로도 곡선 (`TIME_COL` 지정 시)

## 피로도 곡선 사용법

`TIME_COL`에 "플레이 시작 후 몇 분" 컬럼을 지정하면:
- 시간대별 평균 Likert 점수 변화를 시각화
- 점수 하락 = 피로도 증가 신호
- "몇 분 만에 조작에 피로를 느끼는가"를 수치로 확인

## 입력 CSV 예시

```
respondent,minute,q1,q2,q3,q4,q5
user01,5,5,4,5,4,5
user02,10,4,3,4,3,4
user03,15,3,2,3,3,2
user04,20,2,2,2,2,1
```

## Cronbach α 해석 기준

| α 범위 | 판정 |
|---|---|
| α ≥ 0.9 | Excellent |
| α ≥ 0.8 | Good |
| α ≥ 0.7 | Acceptable |
| α ≥ 0.6 | Questionable |
| α < 0.6 | Poor — 문항 재검토 필요 |

## 의존성

`numpy`, `matplotlib` (Agg 백엔드)

## 주의

- `TIME_COL`을 비워두면 피로도 곡선 없이 히스토그램만 생성됩니다.
- Cronbach α는 문항이 2개 이상, 완전 응답자가 2명 이상이어야 계산됩니다.
- Likert 값은 1 이상이어야 합니다. `0`이나 빈 값은 결측으로 처리됩니다.
