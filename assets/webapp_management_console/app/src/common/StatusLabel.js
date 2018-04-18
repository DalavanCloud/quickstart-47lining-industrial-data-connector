import React from 'react'


export default function StatusLabel({ status }) {
    const statusType = status ? status : 'unknown';
    return <div className={`status ${statusType}`}>{statusType}</div>
}
