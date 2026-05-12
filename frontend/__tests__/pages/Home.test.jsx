import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import Home from '../../src/pages/Home'

describe('Home Page', () => {
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
})
