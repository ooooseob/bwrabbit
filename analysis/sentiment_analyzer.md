# sentiment_analyzer

다국어 텍스트 CSV → 감성 분석(긍정/중립/부정) → 언어별 감성 분포 리포트 + 결과 CSV.

## 파라미터 (sentiment_analyzer.json)

| 파라미터 | 기본값 | 설명 |
|---|---|---|
| `INPUT_FILENAME` | `multilingual_reviews.csv` | `_company/data/` 기준 입력 CSV |
| `TEXT_COL` | `"text"` | 감성 분석할 텍스트 컬럼명 |
| `OUTPUT_FILENAME` | `multilingual_reviews_sentiment.md` | 리포트 파일명 |
| `OUTPUT_CSV` | `multilingual_reviews_sentiment.csv` | 결과 CSV 파일명 |
| `BATCH_SIZE` | `32` | 한 번에 처리할 행 수. GPU 있으면 64~128 권장 |
| `MAX_ROWS` | `0` | 최대 처리 행 수. `0`이면 전체. 테스트 시 100 등으로 제한 가능 |

## 출력

- `_company/reports/<OUTPUT_FILENAME>` — 언어별 감성 분포 + 긍/부정 상위 예시
- `_company/data/<OUTPUT_CSV>` — 원본 CSV + `lang` + `sentiment` + `score` 컬럼 추가

## 감성 레이블

| 레이블 | 의미 |
|---|---|
| `positive` | 긍정 |
| `neutral` | 중립 |
| `negative` | 부정 |

## 의존성

`transformers`, `torch` (추론), `langdetect` (언어 감지)

## 주의

- 첫 실행 시 `cardiffnlp/twitter-xlm-roberta-base-sentiment` 모델 (~280MB) 자동 다운로드.
- GPU 없으면 CPU 추론으로 동작하지만 속도가 느립니다. `MAX_ROWS`로 제한 권장.
- Steam 리뷰 분석 시 `topic_modeler`와 함께 사용하면 긍/부정 키워드를 함께 파악 가능.
