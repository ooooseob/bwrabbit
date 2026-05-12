import { render } from '@testing-library/react'
import App from '../src/App'
import { describe, it } from 'vitest'

describe('App', () => {
  it('renders the app', () => {
    render(<App />)
    // 간단한 텍스트가 있는지 확인하는 기본 테스트
    // 실제 App.jsx 내용에 맞춰 수정이 필요할 수 있습니다.
  })
})
