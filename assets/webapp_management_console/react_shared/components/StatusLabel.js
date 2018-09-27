import React from 'react'


export default function StatusLabel({ status, title }) {
    const statusType = status ? status : 'unknown';
    return <div title={title} className={`status ${statusType}`}>{statusType}</div>
}
