import { SchemaItem, HeaderCellProps, TableCellProps, TableRowProps, MongoTableProps} from "./types"
import styles from "./MongoTable.module.css"



function	HeaderCell({label, index, width}:HeaderCellProps) {
    return	<th
        style={{width: width, maxWidth: width}}
    >
        {label}
    </th>
}

function	TableCell({
    value       ,
 	label       ,
	type        ,   
    row_index   ,
    col_index   ,
    width,
}:TableCellProps) {

    let x = 'A very very very long sentence'

    return	<td
        
        style={{width: width, maxWidth: width}}

    >{label === 'goal'  ? x : value}</td>
} 

function	TableRow({
    schema      ,
    data        ,
    row_index   ,
    width       ,
}:TableRowProps) {
		
    
    return	<tr>
        {schema.map((v, i) => {
            return  <TableCell  
                key={`table-data-${row_index}-${i}`}
                value={data[v.label]}
                label={v.label}
                type={v.type}
                row_index={row_index}
                col_index={i}
                width={width}
            />
        })}
    </tr>
}

/**
 * A reusable styled table for MongoDB Data
 */
export  default function    MongoTable({schema_items, data}:MongoTableProps)    {
    const	num_columns	=	schema_items?.length || 0
    const	width		=	`100px`
    return <div className={styles.table_container}>
        <div style={{overflow:'auto', height:'100%', borderRadius: '8px'}}>
    <table 
        className={styles.custom_table}
        style={{width:'100%'}}
    >
        
        <thead 
            style={{width:'100%'}}
        >
            <tr 
                style={{width:'100%'}}
            >
                {schema_items.map(
                    (v, i) => {
                        return  <HeaderCell
                            key={`table-header${i}`}
                            label={v.label}
                            index={i}
                            width={width}
                        />
                    }
                )}
            </tr>
        </thead>

        <tbody>
            {data.map((v, i) => {
                return  <TableRow 
                    key={`table-row-${i}`}
                    schema={schema_items}
                    data={v}
                    row_index={i}
                    width={width}
                />
            })}
        </tbody>
    </table>

        </div>

    </div>  
}