import  {ErrorCalloutProps} from    './types'
import  styles              from    './ErrorCallout.module.css'

export  default function	ErrorCallout({message}:ErrorCalloutProps) {
	return	<div className={styles.error_callout}>
		<div className={styles.error_message}>
			{message}
		</div>
	</div>
}