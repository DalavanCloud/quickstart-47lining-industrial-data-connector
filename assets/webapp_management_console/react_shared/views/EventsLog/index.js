import React, { Component } from 'react'

import EventsLog from './containers/EventsLog'
import Paginated from '../../components/Paginated'


export default class EventsLogContainer extends Component {

    render() {
        return (
            <Paginated
                render={({activePage, sizePerPage, renderPagination, resetActivePage}) => (
                    <EventsLog
                        activePage={activePage}
                        sizePerPage={sizePerPage}
                        renderPagination={renderPagination}
                        resetActivePage={resetActivePage}
                        eventsTypesMapping={this.props.eventsTypesMapping}
                    />
                )}
            />
        )
    }
}
