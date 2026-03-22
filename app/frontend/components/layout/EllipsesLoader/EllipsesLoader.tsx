import { Card } from "@/components/ui"
import {Ellipses} from "@/components/loaders"
import  {EllipsesLoaderProps} from  './types'
import  styles              from    './EllipsesLoader.module.css'

export default function EllipsesLoader({show}:EllipsesLoaderProps) {
    return <div className={show ? styles.show : styles.hide}>
        <Card>
            <Ellipses />
        </Card>
    </div>
}