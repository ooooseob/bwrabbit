import { useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { searchGames } from '../api/game'
import { useDebounce } from '../hooks/useDebounce'
import { useAsync } from '../hooks/useAsync'
import { useInput } from '../hooks/useInput'
import GameCard from '../components/GameCard'
import styles from './Search.module.css'

/**
 * 게임 검색 페이지 컴포넌트
 */
export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [keyword, onChangeKeyword] = useInput(searchParams.get('q') ?? '')
  const { execute, loading, data, error, setData: setGames } = useAsync(searchGames)
  const games = data || []

  const debounced = useDebounce(keyword, 500)

  useEffect(() => {
    if (!debounced.trim()) {
      setGames([])
      return
    }
    execute(debounced)
  }, [debounced, execute, setGames])

  /**
   * 검색어 입력 변경 이벤트 핸들러
   */
  const handleChange = e => {
    onChangeKeyword(e)
    const v = e.target.value
    setSearchParams(v ? { q: v } : {})
  }

  return (
    <main className={styles.main}>
      <div className={styles.searchBar}>
        <input
          className={styles.input}
          type='text'
          placeholder='게임 이름 검색...'
          value={keyword}
          onChange={handleChange}
          autoFocus
        />
      </div>

      {loading && <p className={styles.status}>검색 중...</p>}
      {error && <p className={styles.error}>{error}</p>}
      {!loading && !error && games.length === 0 && debounced && (
        <p className={styles.status}>결과가 없습니다.</p>
      )}

      <div className={styles.grid}>
        {games.map(g => (
          <GameCard key={g.steamAppId} game={g} />
        ))}
      </div>
    </main>
  )
}
