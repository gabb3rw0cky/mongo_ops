import { ChangeEvent } from "react";
import {ButtonProps} from "@/components/ui"

/**
 * Properties for a customizable input box component.
 * @typedef {object} InputBoxProps
 * @property {string} value - The current value of the input box.
 * @property {string} type - The HTML input type.
 * @property {(e: ChangeEvent<HTMLInputElement>) => void} onChange - Callback function invoked when the input value changes.
 * @property {string} fontSize - Font size for the input text.
 * @property {boolean} readOnly - Whether the input box is read-only.
 * @property {ButtonProps} [button] - Optional button component.
 */
export  type    InputBoxProps   =   {
    value       :   string
    type        :   string
    onChange    :   (e:ChangeEvent<HTMLInputElement>) => void
    fontSize    :   string
    readOnly    :   boolean
    button      ?:  ButtonProps
}