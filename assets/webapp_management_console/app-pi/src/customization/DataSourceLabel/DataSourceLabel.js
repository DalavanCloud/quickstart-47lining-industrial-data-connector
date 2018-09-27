import React from 'react'


const dataSourceAbbreviation = {
    all: 'A/S',
    archive: 'A',
    snapshot: 'S'
}

const dataSourceDescription = {
    all: 'Archive and Snapshot',
    archive: 'Archive',
    snapshot: 'Snapshot'
}

export default function DataSourceLabel({ status }) {

    const dataSource = status.archive === 'subscribed' && status.snapshot === 'subscribed'
        ? 'all'
        : status.archive === 'subscribed'
            ? 'archive'
            : status.snapshot === 'subscribed'
                ? 'snapshot'
                : null
    return 'archive' in status &&
        'snapshot' in status &&
        (dataSource ? <abbr className={`data-source ${dataSource}`} title={dataSourceDescription[dataSource]}>{dataSourceAbbreviation[dataSource]}</abbr> : null)
}
