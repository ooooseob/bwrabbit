import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { useAsync } from '../../src/hooks/useAsync'

describe('useAsync', () => {
  it('성공 시 데이터를 반환하고 상태를 업데이트해야 한다', async () => {
    const mockData = { id: 1, title: 'Test Game' }
    const mockFn = vi.fn().mockResolvedValue(mockData)
    const { result } = renderHook(() => useAsync(mockFn))

    expect(result.current.loading).toBe(false)
    expect(result.current.data).toBe(null)

    let res
    await act(async () => {
      res = await result.current.execute('arg1', 'arg2')
    })

    expect(res).toEqual(mockData)
    expect(result.current.data).toEqual(mockData)
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe(null)
    expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2')
  })

  it('실패 시 에러 메시지를 설정해야 한다', async () => {
    const errorResponse = {
      response: {
        data: {
          message: '서버 에러 발생',
        },
      },
    }
    const mockFn = vi.fn().mockRejectedValue(errorResponse)
    const { result } = renderHook(() => useAsync(mockFn))

    await act(async () => {
      try {
        await result.current.execute()
      } catch {
        // ignore
      }
    })

    expect(result.current.error).toBe('서버 에러 발생')
    expect(result.current.loading).toBe(false)
    expect(result.current.data).toBe(null)
  })

  it('기본 에러 메시지를 반환해야 한다', async () => {
    const mockFn = vi.fn().mockRejectedValue(new Error('네트워크 오류'))
    const { result } = renderHook(() => useAsync(mockFn))

    await act(async () => {
      try {
        await result.current.execute()
      } catch {
        // ignore
      }
    })

    expect(result.current.error).toBe('네트워크 오류')
  })
  it('나중에 시작된 요청이 먼저 끝나더라도, 가장 마지막에 시작된 요청의 데이터가 유지되어야 한다', async () => {
    let callCount = 0
    const mockFn = vi.fn().mockImplementation(async id => {
      const currentCall = ++callCount
      // 첫 번째 호출은 200ms, 두 번째 호출은 50ms 대기
      const delay = currentCall === 1 ? 200 : 50
      await new Promise(resolve => setTimeout(resolve, delay))
      return `data for ${id}`
    })

    const { result } = renderHook(() => useAsync(mockFn))

    // 첫 번째 요청 시작 (Req 1)
    const p1 = act(async () => {
      await result.current.execute('first')
    })

    // 약간 대기 후 두 번째 요청 시작 (Req 2)
    await new Promise(resolve => setTimeout(resolve, 20))
    const p2 = act(async () => {
      await result.current.execute('second')
    })

    await Promise.all([p1, p2])
    expect(result.current.data).toBe('data for second')
  })
})
