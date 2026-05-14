# topic_modeler

텍스트 컬럼 → LDA 주제 모델링 → 주제별 상위 단어 + 문서별 주제 배정 CSV. 외부 API 없음.

## 파라미터 (topic_modeler.json)

| 파라미터 | 기본값 | 설명 |
|---|---|---|
| `INPUT_FILENAME` | `multilingual_reviews.csv` | `_company/data/` 기준 입력 CSV |
| `TEXT_COL` | `"text"` | 분석할 텍스트 컬럼명 |
| `N_TOPICS` | `3` | 추출할 주제 수 |
| `N_TOP_WORDS` | `10` | 주제당 상위 단어 수 |
| `MAX_FEATURES` | `500` | CountVectorizer 최대 어휘 크기 |
| `MAX_ITER` | `20` | LDA 최대 반복 횟수 |
| `OUTPUT_FILENAME` | `reviews_topics.md` | 리포트 파일명 |
| `OUTPUT_CSV` | `reviews_topics.csv` | dominant_topic 컬럼 추가 CSV |

## 출력

- `_company/reports/<OUTPUT_FILENAME>` — 주제별 상위 단어 표 + 문서별 주제 배정 요약
- `_company/data/<OUTPUT_CSV>` — 원본 CSV + `dominant_topic` + `topic_prob` 컬럼 추가

## 언어 지원

언어 자동 감지 후 `token_pattern` 자동 선택:
- 한국어(`ko`): `[가-힣]{2,}` (형태소 분석 없음 — 어절 단위)
- 일본어(`ja`): `[ぁ-んァ-ヶ一-龯]{2,}`
- 중국어(`zh`): `[一-龯]{2,}`
- 영어(`en`): `\b[a-zA-Z]{3,}\b` + 영어 불용어 제거

## 의존성

`scikit-learn` (필수), `langdetect` (언어 감지 — 미설치 시 영어로 폴백)

## 주의

- `N_TOPICS` 값에 따라 결과가 크게 달라집니다. 여러 값을 시도해 보세요.
- 주제 이름은 자동 부여되지 않습니다. 상위 단어를 보고 직접 해석하세요.
- 영어 텍스트에 최적화되어 있습니다. 한국어는 정밀도가 낮을 수 있습니다.
