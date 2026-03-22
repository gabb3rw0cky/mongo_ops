import { useState, ChangeEvent } from "react";
import { InputBox } from "@/components/ui/"
import { Eye, EyeOff } from 'lucide-react';

type    ProtectedInputProps   =   {
    value       :   string
    onChange    :   (e:ChangeEvent<HTMLInputElement>) => void
    fontSize    :   string
    readOnly    ?:   boolean
}

export default function ProtectedInput({value, onChange, fontSize, readOnly=false}:ProtectedInputProps) {
    const   [ visible    , set_visible   ]   =   useState<boolean>(false)

    const   on_click_button     =   ()  =>  {
        set_visible(prev => !prev)
    }
    
    return  <InputBox 
        value		=	{value}
        type		=	{visible ? 'text' : 'password'}
        onChange	=	{onChange}
        fontSize	=	{fontSize}
        button		=	{{
            children	:	visible ? <EyeOff size={18} /> : <Eye size={14} />,
            onClick		:	on_click_button,
        }}
        readOnly    =   {readOnly}
    />
}