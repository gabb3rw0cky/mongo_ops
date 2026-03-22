import { ChangeEvent,Dispatch, useRef, useState } from "react";
import {Button, ButtonProps} from "@/components/ui"
import styles from "./NumberInput.module.css"
import { Plus, Minus } from 'lucide-react';

type    NumberInputProps   =   {
    value       :   number
    set_value   :   Dispatch<React.SetStateAction<number>>
    fontSize    :   string
    readOnly    :   boolean
    on_change   ?:  () => void
    min         ?:  number
    max         ?:  number
}

export default  function NumberInput(
    {
        value, set_value, fontSize, readOnly,
        on_change,
        min=undefined,
        max=undefined,
    }:NumberInputProps
) {
    // const   [value, set_value] = useState<number>(0)

    const _on_change = (e:ChangeEvent<HTMLInputElement>) => {
        set_value(Number(e.target.value.replace(/[^0-9]/g, "")))
        if (on_change) {
            on_change()
        }
    }

    const   increase    =   ()  =>  {
        set_value(v  => v + 1)
        if (on_change) {
            on_change()
        }
    }

    const   decrease    =   ()  =>  {
        set_value(v => v - 1)
        if (on_change) {
            on_change()
        }
    }

    function    CustomeButton({children, onClick,disabled}:ButtonProps) {
        return  <Button 
            children={children}
            onClick={onClick}
            padding_y="2px"
            padding_x="4px"
            borderRadius="4px"
            disabled={disabled}
        />
    }

    return  <div className="w-full flex flex-row gap-2">
        <div className="w-full">
            <input 
                value={value}
                type='text'
                min={min}
                max={max}
                step="1"
                onChange={_on_change}
                className={styles.mongo_input}
                style={{fontSize:fontSize, width:'100%'}}
                disabled={readOnly}
            />

        </div>
        <div>
            <CustomeButton 
                children={<Plus size={10}/>}
                onClick={increase}
            disabled={value===max}
            />
            <CustomeButton 
                children={<Minus size={10}/>}
                onClick={decrease}
            disabled={value===min}
            />
            
        </div> 
        
    </div>
}