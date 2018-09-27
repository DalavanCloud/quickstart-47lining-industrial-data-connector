import React from 'react'

import StatusLabel from '../../../components/StatusLabel'


export default function EventFeedGroupsTableRow({ feedGroup }) {
    return (
        <tr key={feedGroup.id}>
            <td>{feedGroup.id + 1}</td>
            <td><div className="feed-group">{feedGroup.feeds.join(', ')}</div></td>
            <td><StatusLabel title={feedGroup.error_message} status={feedGroup.status} /></td>
        </tr>
    )
}
