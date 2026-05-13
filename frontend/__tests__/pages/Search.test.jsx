import { vi, describe, it, expect } from 'vitest'

// API 모킹
vi.mock('../../src/api/game', () => ({
  searchGames: vi.fn(() => Promise.resolve([])),
}))

import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Search from '../../src/pages/Search'

describe('Search Page', () => {
  it('renders search page with input field', async () => {
    render(
      <MemoryRouter>
        <Search />
      </MemoryRouter>
    )
    expect(await screen.findByPlaceholderText(/게임 이름 검색/i)).toBeDefined()
  })
})
