import {CardProps} from "./types"
import styles from "./Card.module.css"

export default function Card({children}:CardProps) {
    return  <div className={styles.card}>
        {children}
    </div>
}