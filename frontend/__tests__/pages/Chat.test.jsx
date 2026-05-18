import { vi, describe, it, expect } from 'vitest'

// API 모킹
vi.mock('../../src/api/game', () => ({
  sendQuery: vi.fn(),
}))

import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Chat from '../../src/pages/Chat'

describe('Chat Page', () => {
  it('renders chat page with initial assistant message', () => {
    render(
      <MemoryRouter>
        <Chat />
      </MemoryRouter>
    )
    expect(screen.getByText(/AI 게임 분석/i)).toBeDefined()
    expect(screen.getByText(/안녕하세요! 게임에 대해 무엇이든 물어보세요/i)).toBeDefined()
  })

  it('renders input area and send button', () => {
    render(
      <MemoryRouter>
        <Chat />
      </MemoryRouter>
    )
    expect(screen.getByPlaceholderText(/게임에 대해 질문하세요/i)).toBeDefined()
    expect(screen.getByRole('button', { name: /전송/i })).toBeDefined()
  })
})
