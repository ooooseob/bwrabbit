import { vi, describe, it, expect } from 'vitest'

// API 모킹을 최상단에서 수행 (Hoisting 보장)
vi.mock('../../src/api/game', () => ({
  getGame: vi.fn(() => new Promise(() => {})), // 로딩 상태 유지를 위해 해결되지 않는 프로미스 반환
}))

import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import GameDetail from '../../src/pages/GameDetail'

describe('GameDetail Page', () => {
  it('renders loading state initially', async () => {
    render(
      <MemoryRouter initialEntries={['/game/570']}>
        <Routes>
          <Route path='/game/:steamAppId' element={<GameDetail />} />
        </Routes>
      </MemoryRouter>
    )
    expect(await screen.findByText(/불러오는 중/i)).toBeDefined()
  })
})
