/**
 * A set of properties for a customizable button component.
 * @typedef {object} ButtonProps
 * @property {React.ReactNode} children - The content inside the button.
 * @property {function(): void} onClick - Callback function invoked when the button is clicked.
 * @property {string} [padding_y] - Optional vertical padding.
 * @property {string} [padding_x] - Optional horizontal padding.
 * @property {string} [borderRadius] - Optional border radius for the button corners.
 * @property {string} [font_size] - Optional font size for button text.
 * @property {boolean} [disabled] - Whether the button is disabled and non-interactive.
 */
export type    ButtonProps     =   {
    children        :   React.ReactNode
    onClick         :   () => void
    padding_y       ?:  string
    padding_x       ?:  string
    borderRadius    ?:  string
    font_size       ?:  string
    disabled        ?:  boolean
}