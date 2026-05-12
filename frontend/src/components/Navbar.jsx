import { Link, useLocation } from 'react-router-dom'
import styles from './Navbar.module.css'

/**
 * 네비게이션 메뉴 구성 목록
 * @type {NavItem[]}
 */
const NAV = [
  { to: '/', label: '홈' },
  { to: '/search', label: '게임 검색' },
  { to: '/fetch', label: '게임 등록' },
  { to: '/chat', label: 'AI 분석' },
]

/**
 * 애플리케이션의 상단 네비게이션 바 컴포넌트
 *
 * 브랜드 로고와 메인 메뉴 링크들을 렌더링하며,
 * 현재 브라우저의 위치(location)를 확인하여 활성화된 메뉴에 스타일을 적용합니다.
 *
 * @component
 * @returns {import('react').JSX.Element} Navbar 컴포넌트
 */
export default function Navbar() {
  const { pathname } = useLocation()
  return (
    <nav className={styles.nav}>
      <Link to='/' className={styles.logo}>
        <span className={styles.logoAccent}>g</span>Web2
      </Link>
      <ul className={styles.links}>
        {NAV.map(({ to, label }) => (
          <li key={to}>
            <Link
              to={to}
              className={pathname === to ? `${styles.link} ${styles.active}` : styles.link}
            >
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  )
}
