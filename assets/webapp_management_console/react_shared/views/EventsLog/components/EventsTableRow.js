import React from 'react'
import { Link } from 'react-router-dom'

import { formatTimestamp } from '../../../utils'
import StatusLabel from '../../../components/StatusLabel'
import AttributesList from './AttributesList'


export default function EventsTableRow({ event, eventsTypesMapping }) {
    return (
        <tr key={event.update_timestamp}>
            <td>{formatTimestamp(event.update_timestamp)}</td>
            <td>{eventsTypesMapping[event.type]}</td>
            <td>
                <ul>
                    <AttributesList event={event} />
                    {
                        event.number_of_feeds
                            && <li><Link className="browse-feeds-link" to={`/event/${event.id}`}>Browse feeds</Link></li>
                    }
                </ul>
            </td>
            <td><StatusLabel status={event.status} /></td>
        </tr>
    )
}
