import  {InputRowProps}     from    './types'
import {Card} from "@/components/ui"
import  styles              from    './InputRow.module.css'

export default function	InputRow(
	{label, input_element, action_button, show=true}:InputRowProps
) {
    return  <div className={show ? styles.show : styles.hide}>
        <Card 
            children    =   {<div>
                    
                    <div className={styles.label_div}>{label}</div>
                    
                    <div className={styles.input_row}>
                        
                        <div className={styles.input_div}>
                            {input_element}
                        </div>
                        
                        <div className={styles.button_div}>
                            {action_button}
                        </div>
                    
                    </div>
                
                </div>

            }
        />
    </div>
}