import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useDebounce } from '../../src/hooks/useDebounce'

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('지연 시간 후에 값이 업데이트되어야 한다', () => {
    const { result, rerender } = renderHook(({ value, delay }) => useDebounce(value, delay), {
      initialProps: { value: 'initial', delay: 400 },
    })

    expect(result.current).toBe('initial')

    // 값 변경
    rerender({ value: 'updated', delay: 400 })
    expect(result.current).toBe('initial') // 아직 업데이트 전

    // 시간 흐름 (399ms)
    act(() => {
      vi.advanceTimersByTime(399)
    })
    expect(result.current).toBe('initial')

    // 시간 흐름 (1ms 추가)
    act(() => {
      vi.advanceTimersByTime(1)
    })
    expect(result.current).toBe('updated')
  })

  it('중간에 값이 변경되면 타이머가 재설정되어야 한다', () => {
    const { result, rerender } = renderHook(({ value, delay }) => useDebounce(value, delay), {
      initialProps: { value: 'initial', delay: 400 },
    })

    rerender({ value: 'first', delay: 400 })

    act(() => {
      vi.advanceTimersByTime(200)
    })
    expect(result.current).toBe('initial')

    // 200ms 시점에서 다시 변경
    rerender({ value: 'second', delay: 400 })

    act(() => {
      vi.advanceTimersByTime(200)
    })
    expect(result.current).toBe('initial') // 아직 400ms 안 지남 (총 200 + 200)

    act(() => {
      vi.advanceTimersByTime(200)
    })
    expect(result.current).toBe('second')
  })
})
