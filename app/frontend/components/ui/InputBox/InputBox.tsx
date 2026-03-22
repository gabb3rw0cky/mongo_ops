import {Button} from "@/components/ui"
import styles from "./InputBox.module.css"
import  {InputBoxProps} from './types'

/**
 * InputBox is a reusable styled input component with optional inline action button.
 */
export default  function InputBox(
    {value, type, onChange, fontSize, readOnly, button}:InputBoxProps
) {

    return  <div className="w-full flex flex-row items-center gap-2">
        <div className="w-[100%]">
            <input 
                value={value}
                type={type}
                onChange={onChange}
                className={styles.mongo_input}
                style={{fontSize:fontSize, width:'100%'}}
                disabled={readOnly}
            />
        </div>
        {button && <div>
            <Button 
                children={button.children}
                onClick={button.onClick}
                padding_x="5px"
                padding_y="3px"
                borderRadius="6px"
            />
        </div>}
    </div>
}