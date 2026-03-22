/**
 * Properties for a dropdown option.
 * @typedef {object} DropdownOption
 * @property {string} value - The actual value of option.
 * @property {string} label - The label ot be displayed.
 */
export type DropdownOption = {
    value   :   string;
    label   :   string;
};

/**
 * Properties for a customizable dropdown component.
 * @typedef {object} DropdownProps
 * @property {DropdownOption} value - The current label, value pair of the dropdown.
 * @property {(e: ChangeEvent<HTMLInputElement>) => void} onChange - Callback function invoked when new item is selected.
 * @property {DropdownOption[]} options - List of options to select from.
 * @property {string} fontSize - font size.
 */
export type DropdownProps = {
    value       :   DropdownOption;
    onChange    :   (option:DropdownOption) => void
    options     :   DropdownOption[];
    fontSize    :   string
};