import { useState, useEffect } from 'react'

/**
 * 일정 시간 동안 값의 변화가 없으면 최종 값을 반환합니다.
 * @param {any} value - debounce를 적용할 값
 * @param {number} delay - 지연 시간 (ms, 기본값 400ms)
 * @returns {any} - debounce가 적용된 값
 */
export function useDebounce(value, delay = 400) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return debounced
}
