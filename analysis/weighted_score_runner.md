# weighted_score_runner

항목(장르 등) × 지표 점수 CSV → 지표별 가중치 적용 + 방향 반전 → 가중 합산 순위 리포트 + 바 차트 PNG.

## 파라미터 (weighted_score_runner.json)

| 파라미터 | 기본값 | 설명 |
|---|---|---|
| `INPUT_FILENAME` | `genre_scores.csv` | `_company/data/` 기준 입력 CSV |
| `ITEM_COL` | `"genre"` | 항목을 식별하는 컬럼명 (장르명, 제품명 등) |
| `SCORE_COLS` | `["input_precision", ...]` | 점수가 있는 지표 컬럼 목록 |
| `WEIGHTS` | `{}` (모두 1.0) | 지표별 가중치 딕셔너리. 미지정 컬럼은 1.0 |
| `HIGHER_IS_BETTER` | `{}` (모두 true) | `false`이면 해당 지표 반전 적용 (낮을수록 유리) |
| `NORMALIZE` | `true` | min-max 정규화 여부. `false`면 원본 값 그대로 가중 합산 |
| `OUTPUT_FILENAME` | `genre_scores_weighted.md` | 리포트 파일명 |
| `OUTPUT_PLOT` | `genre_scores_weighted.png` | 바 차트 PNG 파일명 |

## 출력

- `_company/reports/<OUTPUT_FILENAME>` — 지표 설정 표 + 항목별 원본 점수 + 최종 순위 테이블
- `_company/reports/<OUTPUT_PLOT>` — 항목별 최종 점수 수평 바 차트 (녹색=상위, 빨강=하위)

## 점수 계산 방식

1. 각 지표를 min-max 정규화 → [0, 1] (`NORMALIZE: true` 기준)
2. `HIGHER_IS_BETTER: false` 지표는 `1 − 정규화값` 으로 반전
3. `최종 점수 = Σ(조정값 × 가중치) / Σ가중치`

## 의존성

`numpy`, `matplotlib` (Agg 백엔드)

## 기본 설정 기준 (게임 장르 판단 4개 지표)

| 지표 컬럼 | 방향 | 가중치 | 의미 |
|---|---|---:|---|
| `input_precision` | 낮을수록 유리 | 1.0 | 입력 정밀도 의존성 (낮아야 웹캠/음성 오차 허용) |
| `marketing_conversion` | 높을수록 유리 | 1.5 | 마케팅 전환 효율 (시각적 직관성) |
| `hardware_friction` | 낮을수록 유리 | 1.0 | 하드웨어 세팅 마찰 (낮아야 빠른 시작) |
| `core_loop` | 높을수록 유리 | 1.5 | 기술 기반 핵심 루프 기여도 |

## 주의

- 점수는 입력된 항목 간 **상대 비교**입니다. 항목이 추가/제거되면 순위가 바뀝니다.
- 결측값(`""`)이 있는 지표는 해당 항목 계산에서 자동 제외됩니다.
- 항목이 1개뿐이면 정규화 시 모든 점수가 0.5로 동일해집니다 (비교 불가).
