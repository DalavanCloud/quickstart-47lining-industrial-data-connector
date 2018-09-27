import React from 'react'

import { DeleteFilterIcon } from '../../components/icons'


export default function Filter({ filter, onDelete }) {
    return (
        <div className="chosen-filter">
            <h3>{`${filter.type} ${filter.parameter}:`}</h3><span> {filter.value}</span>
            <button onClick={onDelete} className="close"><DeleteFilterIcon /></button>
        </div>
    )
}
