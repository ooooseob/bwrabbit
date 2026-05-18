import styles from './Pagination.module.css'

/**
 * 재사용 가능한 페이지네이션 컴포넌트
 *
 * @component
 * @param {Object} props
 * @param {number} props.currentPage - 현재 페이지 번호 (0-indexed)
 * @param {number} props.totalPages - 전체 페이지 수
 * @param {Function} props.onPageChange - 페이지 변경 핸들러 함수
 * @returns {import('react').JSX.Element|null} Pagination 컴포넌트
 */
export default function Pagination({ currentPage, totalPages, onPageChange }) {
  if (totalPages <= 1) return null

  return (
    <div className={styles.pagination}>
      <button
        className={styles.pageBtn}
        onClick={() => onPageChange(Math.max(currentPage - 1, 0))}
        disabled={currentPage === 0}
      >
        이전
      </button>

      {Array.from({ length: totalPages }, (_, i) => (
        <button
          key={i}
          className={`${styles.pageBtn} ${currentPage === i ? styles.activePageBtn : ''}`}
          onClick={() => onPageChange(i)}
        >
          {i + 1}
        </button>
      ))}

      <button
        className={styles.pageBtn}
        onClick={() => onPageChange(Math.min(currentPage + 1, totalPages - 1))}
        disabled={currentPage === totalPages - 1}
      >
        다음
      </button>
    </div>
  )
}
