import React, { Fragment } from 'react'

import StatusLabel from './StatusLabel'


export default function SubscriptionStatusLabel({ status, DataSourceLabel }) {
    const aggregatedStatus = Object.values(status).includes('pending')
        ? 'pending'
        : Object.values(status).includes('subscribed')
            ? 'subscribed' : 'unsubscribed'
    const statusLabelTitle = Object.keys(status).length === 1
        ? `Subscription status: ${Object.values(status)[0]}`
        : `Subscription status: ${Object.entries(status).map(([k, v]) => `${k} - ${v}`).join(', ')}`

    return (
        <Fragment>
            <StatusLabel
                status={aggregatedStatus}
                title={statusLabelTitle}
            />
            {
                <DataSourceLabel status={status} />
            }
        </Fragment>
    )
}
