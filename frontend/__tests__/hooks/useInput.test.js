import { renderHook, act } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { useInput } from '../../src/hooks/useInput'

describe('useInput', () => {
  it('초기값을 가져야 한다', () => {
    const { result } = renderHook(() => useInput('hello'))
    expect(result.current[0]).toBe('hello')
  })

  it('onChange로 값을 변경할 수 있어야 한다', () => {
    const { result } = renderHook(() => useInput(''))
    act(() => {
      result.current[1]({ target: { value: 'world' } })
    })
    expect(result.current[0]).toBe('world')
  })

  it('reset으로 초기화할 수 있어야 한다', () => {
    const { result } = renderHook(() => useInput('initial'))
    act(() => {
      result.current[1]({ target: { value: 'changed' } })
    })
    expect(result.current[0]).toBe('changed')
    act(() => {
      result.current[2]()
    })
    expect(result.current[0]).toBe('initial')
  })

  it('setValue로 직접 값을 변경할 수 있어야 한다', () => {
    const { result } = renderHook(() => useInput(''))
    act(() => {
      result.current[3]('direct')
    })
    expect(result.current[0]).toBe('direct')
  })
})
