import React, { Component } from 'react'

import EventsTableRow from './EventsTableRow'


export default class EventsTable extends Component {
    render() {
        return (
            <div className={`table-holder ${this.props.loading ? 'inactive' : ''}`}>
                <table className="checkbox-table">
                    <tbody>
                        <tr>
                            <th>Timestamp</th>
                            <th>Type</th>
                            <th>Attributes</th>
                            <th>Status</th>
                        </tr>
                        {
                            this.props.events.map(event => (
                                <EventsTableRow eventsTypesMapping={this.props.eventsTypesMapping} key={`event-${event.id}`} event={event} />
                            ))
                        }
                    </tbody>
                </table>
            </div>
        )
    }
}
