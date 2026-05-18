import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import Home from '../../src/pages/Home'

const { mockGetGamesPaged } = vi.hoisted(() => ({
  mockGetGamesPaged: vi.fn(),
}))

// API 모킹
vi.mock('../../src/api/game', () => ({
  getGamesPaged: mockGetGamesPaged,
}))

describe('Home Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // 기본 모킹 데이터 설정 (에러 방지용)
    mockGetGamesPaged.mockResolvedValue({
      content: [],
      number: 0,
      totalPages: 1,
      totalElements: 0,
      size: 8,
      first: true,
      last: true,
    })
  })

  it('renders home page with correct title', () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    )
    expect(screen.getByRole('heading', { name: /게임을 탐색하세요/i })).toBeDefined()
  })

  it('renders search input and button', () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    )
    expect(screen.getByPlaceholderText(/게임 이름을 입력하세요/i)).toBeDefined()
    expect(screen.getByRole('button', { name: /^검색$/ })).toBeDefined()
  })

  it('renders feature cards', () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    )
    expect(screen.getByText('게임 검색')).toBeDefined()
    expect(screen.getByText('AI 분석')).toBeDefined()
    expect(screen.getByText('게임 등록')).toBeDefined()
  })

  it('fetches and renders registered games list on load', async () => {
    mockGetGamesPaged.mockResolvedValueOnce({
      content: [
        {
          id: 1,
          steamAppId: 570,
          name: 'Dota 2',
          shortDescription: 'MOBA game',
          headerImage: 'dota2.jpg',
          priceFinal: 0,
        },
        {
          id: 2,
          steamAppId: 730,
          name: 'Counter-Strike 2',
          shortDescription: 'FPS game',
          headerImage: 'cs2.jpg',
          priceFinal: 0,
        },
      ],
      number: 0,
      totalPages: 3,
      totalElements: 6,
      size: 2,
      first: true,
      last: false,
    })

    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    )

    // "등록된 게임" 섹션 제목 검증
    expect(await screen.findByRole('heading', { name: /등록된 게임/i })).toBeDefined()

    // 게임 카드 렌더링 확인
    expect(await screen.findByText('Dota 2')).toBeDefined()
    expect(await screen.findByText('Counter-Strike 2')).toBeDefined()
  })

  it('renders pagination controls and handles page navigation', async () => {
    mockGetGamesPaged.mockResolvedValueOnce({
      content: [
        {
          id: 1,
          steamAppId: 570,
          name: 'Dota 2',
          shortDescription: 'MOBA game',
          headerImage: 'dota2.jpg',
          priceFinal: 0,
        },
      ],
      number: 0,
      totalPages: 3,
      totalElements: 3,
      size: 1,
      first: true,
      last: false,
    })

    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    )

    // 페이지네이션 컨트롤 존재 여부 확인
    expect(await screen.findByRole('button', { name: /이전/i })).toBeDefined()
    expect(screen.getByRole('button', { name: /다음/i })).toBeDefined()
    expect(screen.getByRole('button', { name: '2' })).toBeDefined()

    // 첫 페이지이므로 "이전" 버튼은 비활성화 상태여야 함
    expect(screen.getByRole('button', { name: /이전/i }).hasAttribute('disabled')).toBe(true)

    // 다음 페이지 데이터 모킹
    mockGetGamesPaged.mockResolvedValueOnce({
      content: [
        {
          id: 2,
          steamAppId: 730,
          name: 'Counter-Strike 2',
          shortDescription: 'FPS game',
          headerImage: 'cs2.jpg',
          priceFinal: 0,
        },
      ],
      number: 1,
      totalPages: 3,
      totalElements: 3,
      size: 1,
      first: false,
      last: false,
    })

    // "다음" 버튼 클릭
    const nextBtn = screen.getByRole('button', { name: /다음/i })
    nextBtn.click()

    // 2페이지 게임 렌더링 확인
    expect(await screen.findByText('Counter-Strike 2')).toBeDefined()
    expect(mockGetGamesPaged).toHaveBeenCalledWith(1, 8)
  })
})
