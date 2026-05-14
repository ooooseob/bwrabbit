# radar_chart_runner

항목(장르 등) × 지표 점수 CSV → 레이더(스파이더) 차트 PNG + 지표별 점수 비교 리포트.

## 파라미터 (radar_chart_runner.json)

| 파라미터 | 기본값 | 설명 |
|---|---|---|
| `INPUT_FILENAME` | `genre_scores.csv` | `_company/data/` 기준 입력 CSV |
| `ITEM_COL` | `"genre"` | 항목을 식별하는 컬럼명 (장르명, 제품명 등) |
| `SCORE_COLS` | `["input_precision", ...]` | 지표 컬럼 목록 (레이더 축). **3개 이상 필수** |
| `HIGHER_IS_BETTER` | `{}` (모두 true) | `false`이면 차트에서 반전 표시 (낮을수록 바깥) |
| `NORMALIZE` | `true` | min-max 정규화 여부. `false`면 원본 값 그대로 |
| `MAX_ITEMS` | `8` | 차트에 표시할 최대 항목 수. 초과 시 앞 N개만 사용 |
| `OUTPUT_FILENAME` | `genre_scores_radar.md` | 리포트 파일명 |
| `OUTPUT_PLOT` | `genre_scores_radar.png` | 레이더 차트 PNG 파일명 |

## 출력

- `_company/reports/<OUTPUT_FILENAME>` — 지표 설정 표 + 항목별 정규화 점수 테이블 + 차트 참조
- `_company/reports/<OUTPUT_PLOT>` — 항목별 다각형이 겹쳐진 레이더 차트 (항목당 다른 색상)

## 차트 읽는 법

- 각 축 = 하나의 지표
- 각 다각형 = 하나의 항목 (장르)
- **바깥으로 뻗을수록 유리**: `HIGHER_IS_BETTER: false` 지표는 자동 반전 처리
- 다각형 면적이 클수록 종합 경쟁력이 높음

## 의존성

`numpy`, `matplotlib` (Agg 백엔드)

## 주의

- `SCORE_COLS`는 **3개 이상** 필요합니다 (레이더 차트 최소 요건).
- 항목이 `MAX_ITEMS` 초과 시 앞 N개만 차트에 표시됩니다.
- 항목이 8개를 초과하면 색상이 반복되어 구분이 어려워집니다.
- `weighted_score_runner`와 같은 입력 CSV를 공유할 수 있습니다.
