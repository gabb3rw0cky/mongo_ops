import { useEffect, useLayoutEffect, useState, ChangeEventHandler, ChangeEvent } from "react";
import { ChevronDown, ChevronUp } from 'lucide-react';
import { DropdownOption, DropdownProps } from "./types"
import { InputBox } from "@/components/ui/"
import styles from "./Dropdown.module.css"

export default function Dropdown({ value, onChange, options, fontSize }:DropdownProps) {
    const   [ show_options  , set_show_options  ]   =   useState<boolean>(false)

    const   on_click_open   =   () =>  {
        set_show_options(true)
    }

    const   on_click_close   =   () =>  {
        set_show_options(false)
    }

    const   on_click_option   =   (option:DropdownOption) =>  {
            onChange(option)
            set_show_options(false)
        }

    function    OptionItem(option:DropdownOption, index:Number) {
        
        return  <div 
            key={`dropdown-item${index}`}
            className={styles.dropdown_option}
            onClick={() => on_click_option(option)}
        >
            {option.label}
        </div>
    }

    function    OptionList()    {

        return  <div className={styles.dropdown_options}>
        {
            options.length === 0
                ?   <div className={styles.dropdown_option_no_hover}>No Items.</div>
                :   options.map(OptionItem)
        }
        </div>
    }

    function    OpenButton()    {
        return  {
                children    :   <ChevronDown size={14}/>,
                onClick     :   on_click_open
            }
    }

    function    CloseButton()    {
        return  {
                children    :   <ChevronUp size={14}/>,
                onClick     :   on_click_close
            }
    }   

    return  <div className={styles.dropdown}>
        <InputBox
            value       =   {value.label}
            type        =   'text'
            onChange    =   {() => {}}
            fontSize    =   {fontSize}
            button      =   {show_options ? CloseButton() : OpenButton()}
            readOnly    =   {true}
        />

        {show_options && OptionList()}
    </div>

}