# Frontend — React

## 스택

- React (JS, not TS) / Vite / React Router 7
- CSS Modules (`.module.css`) — styled-components 금지
- 상태관리: 별도 라이브러리 없음, useState/useEffect 기본 사용
- 테스트: Vitest / React Testing Library
- 포맷팅: Prettier

## 디렉토리 구조

```text
frontend/
├── src/
│   ├── api/          # client.js (axios 인스턴스), game.js (API 함수)
│   ├── components/   # 재사용 컴포넌트 (GameCard, Navbar)
│   ├── hooks/        # 커스텀 훅 (useDebounce, useAsync, useInput)
│   ├── pages/        # 라우트별 페이지 (Chat, Fetch, GameDetail, Home, Search)
│   └── assets/       # 이미지 등 정적 파일
└── __tests__/       # 테스트 코드 (Vitest)
```

## 페이지 목록

| 파일           | 경로        | 역할                           |
| -------------- | ----------- | ------------------------------ |
| Home.jsx       | `/`         | 메인 페이지                    |
| Search.jsx     | `/search`   | 게임 검색                      |
| GameDetail.jsx | `/game/:id` | 게임 상세                      |
| Chat.jsx       | `/chat`     | LLM 질의 채팅                  |
| Fetch.jsx      | `/fetch`    | Steam appid 입력 → 데이터 수집 |

## API 통신

- 백엔드 baseURL: `http://localhost:8080`
- `src/api/client.js` 의 axios 인스턴스 사용, 직접 fetch/axios 호출 금지
- 새 API 함수는 `src/api/game.js` 에 추가

## 컴포넌트 & 코드 규칙

- 컴포넌트 파일과 같은 이름의 `.module.css` 파일 세트로 관리
- props drilling 2단계 이상이면 구조 재검토
- 새 컴포넌트는 `components/`, 페이지 전용은 해당 `pages/` 안에
- 코드 제출 전 반드시 `npm run format` 실행

## 주요 명령어

```bash
npm run dev     # 개발 서버 실행 (http://localhost:5173)
npm run build   # 프로덕션 빌드
npm run test    # 테스트 실행 (Vitest)
npm run lint    # 린트 검사
npm run format  # Prettier 코드 포맷팅
```
