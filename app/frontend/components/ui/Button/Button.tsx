import styles from "./Button.module.css"
import { ButtonProps } from "./types"

/**
 * A reusable styled button component
 */
export default function Button({
    children, 
    onClick,
    padding_y='5px',
    padding_x='10px',
    borderRadius='10px',
    font_size='12px',
    disabled=false
    
}:ButtonProps) {
    return  <button 
        onClick={onClick}
        className={styles.mongo_button}
        style={{
            fontSize:font_size, 
            padding: `${padding_y} ${padding_x}`, 
            height:'fit-content',
            borderRadius: borderRadius,
            // width:width,
        }}
        disabled={disabled}
    >
        {children}
        
    </button>
}