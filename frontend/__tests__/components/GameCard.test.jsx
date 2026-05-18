import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import GameCard from '../../src/components/GameCard'

describe('GameCard', () => {
  const mockGame = {
    steamAppId: '12345',
    name: 'Test Game',
    headerImage: 'test-image.jpg',
    shortDescription: 'This is a test description for the game.',
    positiveReviews: 80,
    negativeReviews: 20,
    priceFinal: 15000,
    genres: ['Action', 'RPG'],
  }

  it('게임 정보를 올바르게 렌더링해야 한다', () => {
    render(
      <MemoryRouter>
        <GameCard game={mockGame} />
      </MemoryRouter>
    )

    expect(screen.getByText('Test Game')).toBeDefined()
    expect(screen.getByText(/This is a test description/)).toBeDefined()
    expect(screen.getByText('호감도 80%')).toBeDefined()
    expect(screen.getByText('₩15,000')).toBeDefined()
    expect(screen.getByText('Action')).toBeDefined()
    expect(screen.getByText('RPG')).toBeDefined()

    const img = screen.getByAltText('Test Game')
    expect(img.getAttribute('src')).toBe('test-image.jpg')
  })

  it('가격이 0일 때 "무료"라고 표시해야 한다', () => {
    const freeGame = { ...mockGame, priceFinal: 0 }
    render(
      <MemoryRouter>
        <GameCard game={freeGame} />
      </MemoryRouter>
    )

    expect(screen.getByText('무료')).toBeDefined()
  })

  it('할인이 활성화되었을 때 할인율과 원가를 함께 렌더링해야 한다', () => {
    const discountGame = { ...mockGame, priceInitial: 30000, priceFinal: 15000 }
    render(
      <MemoryRouter>
        <GameCard game={discountGame} />
      </MemoryRouter>
    )

    expect(screen.getByText('-50%')).toBeDefined()
    expect(screen.getByText('₩30,000')).toBeDefined()
    expect(screen.getByText('₩15,000')).toBeDefined()
  })

  it('상세 페이지로 이동하는 링크를 포함해야 한다', () => {
    render(
      <MemoryRouter>
        <GameCard game={mockGame} />
      </MemoryRouter>
    )

    const link = screen.getByRole('link')
    expect(link.getAttribute('href')).toBe('/game/12345')
  })
})
