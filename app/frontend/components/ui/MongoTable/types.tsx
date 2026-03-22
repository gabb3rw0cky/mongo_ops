/**
 * A single item in a table schema, defining a column.
 * @typedef {object} SchemaItem
 * @property {string} label - The display label for the column.
 * @property {string} type - The type of the column (e.g., "text", "number", "date").
 */
export type	SchemaItem	=	{
	label   :   string
	type    :   string
}

/**
 * Properties for a table header cell component.
 * @typedef {object} HeaderCellProps
 * @property {string} label - The text to display in the header cell.
 * @property {number} index - The index of the column in the table.
 * @property {string} width - The width of the column (e.g., "100px", "10%").
 */
export  type    HeaderCellProps      =   {
    label       :   string
    index       :   number
    width       :   string
}

/**
 * Properties for a table cell component.
 * @typedef {object} TableCellProps
 * @property {any} value - The value to display in the cell.
 * @property {string} label - The label of the column this cell belongs to.
 * @property {string} type - The type of the cell (matches the column type).
 * @property {number} row_index - The index of the row this cell belongs to.
 * @property {number} col_index - The index of the column this cell belongs to.
 * @property {string} width - The width of the column/cell.
 */
export type    TableCellProps  =   {
    value       :   any
 	label       :   string
	type        :   string   
    row_index   :   number
    col_index   :   number
    width       :   string
}

/**
 * Properties for a table row component.
 * @typedef {object} TableRowProps
 * @property {SchemaItem[]} schema - The schema describing each column in the row.
 * @property {any} data - The data object for this row.
 * @property {number} row_index - The index of the row in the table.
 * @property {string} width - The total width of the row.
 */
export  type    TableRowProps   =   {
    schema      :   SchemaItem[]
    data        :   any
    row_index   :   number  
    width       :   string
}

/**
 * Properties for a Mongo-backed table component.
 * @typedef {object} MongoTableProps
 * @property {SchemaItem[]} schema_items - The array of schema items defining each column in the table.
 * @property {any[]} data - The array of data objects to populate the table rows.
 */
export type    MongoTableProps =   {
    schema_items    :   SchemaItem[]
    data            :   any[]
}