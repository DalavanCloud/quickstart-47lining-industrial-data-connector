import React from 'react'
import _ from 'lodash'
import moment from 'moment'

import { formatTimestamp, formatDuration } from '../../../utils'
import { eventAttributesMapping, hiddenAttributes } from '../mappings'


export default function AttributesList({ event }) {

    const attributes = Object.keys(event).filter(
        key => hiddenAttributes.indexOf(key) === -1
    ).map(
        key => Array.isArray(event[key]) ? [key, event[key].join(', ')] : [key, event[key]]
    ).filter(
        ([key, val]) => val
    ).map(
        ([key, val]) => key === 'start_timestamp' ? [key, formatTimestamp(val)] : [key, val]
    ).map(
        ([key, val]) => eventAttributesMapping.hasOwnProperty(key) ? [eventAttributesMapping[key], val] : [key, val]
    ).map(
        ([key, val]) => <li key={key}><label>{_.capitalize(key.replace(/_/g, ' '))}:</label> {val}</li>
    )

    const elapsedMinutes = Math.ceil(
        moment.duration(
            moment(event.update_timestamp).diff(moment(event.start_timestamp))
        ).asMinutes()
    )

    return (
        <ul>
            {attributes}
            {elapsedMinutes > 0 && <li key="elapsed-time">
                <label>Elapsed time:</label> {formatDuration(elapsedMinutes)}
            </li>}
        </ul>
    )
}
