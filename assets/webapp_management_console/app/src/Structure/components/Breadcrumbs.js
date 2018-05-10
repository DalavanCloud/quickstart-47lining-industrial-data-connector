import React from 'react'


export default function Breadcrumbs({ assetId, handleSelect }) {
    const parts = assetId.split('\\');
    const paths = parts.map((part, i) => (
        parts.slice(0, i+1).join('\\')
    ))

    return (
        <ol className="breadcrumb">
            {parts.slice(3, -1).map((crumb, i) => (
                <li key={`breadcrumb-${i}`}>
                    <a title={paths[i+3]} onClick={() => handleSelect(paths[i+3])}>{crumb}</a> <span>{'>'}</span>
                </li>
            ))}
            <li
                className="active"
                onClick={() => handleSelect(paths.slice(-1)[0])}
            >
                <a title={paths.slice(-1)[0]} onClick={() => handleSelect(paths.slice(-1)[0])}>{parts.slice(-1)}</a>
            </li>
        </ol>
    )
}
