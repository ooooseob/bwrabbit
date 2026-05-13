import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import Navbar from '../../src/components/Navbar'

describe('Navbar', () => {
  it('모든 네비게이션 링크를 렌더링해야 한다', () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    )

    expect(screen.getByText('홈')).toBeDefined()
    expect(screen.getByText('게임 검색')).toBeDefined()
    expect(screen.getByText('게임 등록')).toBeDefined()
    expect(screen.getByText('AI 분석')).toBeDefined()
  })

  it('현재 경로에 해당하는 링크에 active 클래스가 적용되어야 한다', () => {
    render(
      <MemoryRouter initialEntries={['/search']}>
        <Navbar />
      </MemoryRouter>
    )

    const searchLink = screen.getByText('게임 검색')
    expect(searchLink.className).toContain('active')
  })
})
