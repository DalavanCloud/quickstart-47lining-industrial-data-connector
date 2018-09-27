import React, { Component } from 'react'

import EventFeedGroupsTableRow from './EventFeedGroupsTableRow'


export default class EventFeedGroupsTable extends Component {
    render() {
        return (
            <div className={`table-holder ${this.props.loading ? 'inactive' : ''}`}>
                <table className="checkbox-table">
                    <tbody>
                        <tr>
                            <th>Group ID</th>
                            <th>Feeds</th>
                            <th>Status</th>
                        </tr>
                        {
                            this.props.feedGroups.map(feedGroup => (
                                <EventFeedGroupsTableRow key={`feed-group-${feedGroup.id}`} feedGroup={feedGroup} />
                            ))
                        }
                    </tbody>
                </table>
            </div>
        )
    }
}
