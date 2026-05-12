import { useState, useCallback } from 'react'

/**
 * 입력 필드의 상태 관리를 위한 훅
 *
 * @param {any} initialValue - 초기값
 * @returns {[any, Function, Function, Function]} [value, onChange, reset, setValue]
 */
export const useInput = initialValue => {
  const [value, setValue] = useState(initialValue)

  const onChange = useCallback(e => {
    setValue(e.target.value)
  }, [])

  const reset = useCallback(() => {
    setValue(initialValue)
  }, [initialValue])

  return [value, onChange, reset, setValue]
}
