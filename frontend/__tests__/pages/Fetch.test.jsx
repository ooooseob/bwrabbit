import { vi, describe, it, expect } from 'vitest'

// API 모킹
vi.mock('../../src/api/game', () => ({
  fetchGame: vi.fn(),
}))

import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Fetch from '../../src/pages/Fetch'

describe('Fetch Page', () => {
  it('renders fetch page with title and description', () => {
    render(
      <MemoryRouter>
        <Fetch />
      </MemoryRouter>
    )
    expect(screen.getByText(/게임 등록/i)).toBeDefined()
    expect(screen.getByText(/Steam App ID를 입력하면/i)).toBeDefined()
  })

  it('renders input field and fetch button', () => {
    render(
      <MemoryRouter>
        <Fetch />
      </MemoryRouter>
    )
    expect(screen.getByPlaceholderText(/Steam App ID \(예: 570\)/i)).toBeDefined()
    expect(screen.getByRole('button', { name: /데이터 수집/i })).toBeDefined()
  })
})
