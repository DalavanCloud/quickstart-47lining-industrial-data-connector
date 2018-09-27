import React, { Component } from 'react'

import EventFeedGroups from './containers/EventFeedGroups'
import Paginated from '../../components/Paginated'


export default class EventsLogContainer extends Component {

    render() {
        return (
            <Paginated
                render={({activePage, sizePerPage, renderPagination, resetActivePage}) => (
                    <EventFeedGroups
                        activePage={activePage}
                        sizePerPage={sizePerPage}
                        renderPagination={renderPagination}
                        resetActivePage={resetActivePage}
                        eventId={this.props.computedMatch.params.eventId}
                    />
                )}
            />
        )
    }
}
