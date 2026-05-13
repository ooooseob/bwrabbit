import { useNavigate } from 'react-router-dom'
import { useInput } from '../hooks/useInput'
import styles from './Home.module.css'

/**
 * 홈 페이지 컴포넌트
 */
export default function Home() {
  const [keyword, onChangeKeyword] = useInput('')
  const navigate = useNavigate()

  /**
   * 검색 폼 제출 이벤트 핸들러
   */
  const handleSearch = e => {
    e.preventDefault()
    if (keyword.trim()) navigate(`/search?q=${encodeURIComponent(keyword.trim())}`)
  }

  return (
    <main className={styles.main}>
      <div className={styles.hero}>
        <h1 className={styles.title}>
          <span className={styles.accent}>게임</span>을 탐색하세요
        </h1>
        <p className={styles.subtitle}>AI 기반 게임 추천 · 분석 · 리뷰 · 게임시장 정보</p>
        <form onSubmit={handleSearch} className={styles.searchForm}>
          <input
            className={styles.searchInput}
            type='text'
            placeholder='게임 이름을 입력하세요...'
            value={keyword}
            onChange={onChangeKeyword}
            autoFocus
          />
          <button type='submit' className={styles.searchBtn}>
            검색
          </button>
        </form>
      </div>

      <div className={styles.features}>
        <FeatureCard
          title='게임 검색'
          desc='게임 이름으로 빠르게 검색. pg_trgm 기반 유사도 검색 지원.'
          icon='🔍'
          to='/search'
        />
        <FeatureCard
          title='AI 분석'
          desc='자연어로 질문하면 AI가 게임을 추천하고 분석합니다.'
          icon='🤖'
          to='/chat'
        />
        <FeatureCard
          title='게임 등록'
          desc='Steam App ID로 게임 데이터를 수집해 DB에 저장합니다.'
          icon='➕'
          to='/fetch'
        />
      </div>
    </main>
  )
}

/**
 * 홈 페이지에서 사용되는 기능 소개 카드 컴포넌트
 *
 * @component
 * @param {Object} props
 * @param {string} props.title - 서비스 제목
 * @param {string} props.desc - 서비스 상세 설명
 * @param {string} props.icon - 표시할 이모지 또는 아이콘
 * @param {string} props.to - 클릭 시 이동할 내부 경로
 * @returns {import('react').JSX.Element} FeatureCard 컴포넌트
 */
function FeatureCard({ title, desc, icon, to }) {
  const navigate = useNavigate()
  return (
    <button className={styles.featureCard} onClick={() => navigate(to)}>
      <span className={styles.featureIcon}>{icon}</span>
      <h3 className={styles.featureTitle}>{title}</h3>
      <p className={styles.featureDesc}>{desc}</p>
    </button>
  )
}
