import { Link } from 'react-router-dom'
import styles from './GameCard.module.css'

/**
 * 개별 게임 정보를 카드 형태로 표시하는 컴포넌트
 *
 * 이미지, 이름, 짧은 설명, 리뷰 기반 호감도, 가격 및 장르 태그를 렌더링합니다.
 * 클릭 시 해당 게임의 상세 페이지로 이동합니다.
 *
 * @component
 * @param {Object} props
 * @param {Game} props.game - 표시할 게임 정보 객체
 * @returns {import('react').JSX.Element} GameCard 컴포넌트
 */
export default function GameCard({ game }) {
  const total = (game.positiveReviews ?? 0) + (game.negativeReviews ?? 0)
  const ratio = total > 0 ? Math.round((game.positiveReviews / total) * 100) : null

  return (
    <Link to={`/game/${game.steamAppId}`} className={styles.card}>
      {game.headerImage && <img src={game.headerImage} alt={game.name} className={styles.img} />}
      <div className={styles.body}>
        <h3 className={styles.name}>{game.name}</h3>
        {game.shortDescription && (
          <p className={styles.desc}>{game.shortDescription.slice(0, 100)}...</p>
        )}
        <div className={styles.meta}>
          {ratio !== null && (
            <span className={ratio >= 70 ? styles.positive : styles.negative}>호감도 {ratio}%</span>
          )}
          {game.priceFinal != null && (
            <div className={styles.priceContainer}>
              {game.priceInitial && game.priceInitial > game.priceFinal ? (
                <>
                  <span className={styles.discountBadge}>
                    -{Math.round(((game.priceInitial - game.priceFinal) / game.priceInitial) * 100)}%
                  </span>
                  <span className={styles.originalPrice}>
                    ₩{game.priceInitial.toLocaleString()}
                  </span>
                  <span className={styles.discountedPrice}>
                    ₩{game.priceFinal.toLocaleString()}
                  </span>
                </>
              ) : (
                <span className={styles.price}>
                  {game.priceFinal === 0 ? '무료' : `₩${game.priceFinal.toLocaleString()}`}
                </span>
              )}
            </div>
          )}
        </div>
        {game.genres?.length > 0 && (
          <div className={styles.tags}>
            {game.genres.slice(0, 3).map(g => (
              <span key={g} className={styles.tag}>
                {g}
              </span>
            ))}
          </div>
        )}
      </div>
    </Link>
  )
}
