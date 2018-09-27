import React, { Component, Fragment } from 'react'

import Loading from '../../../components/Loading'
import apiClient from '../../../apiClient'

import EventFeedGroupsTable from '../components/EventFeedGroupsTable'


class EventsLog extends Component {

    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            feedGroups: [],
            totalItemsCount: 0
        }
    }

    componentDidMount() {
        this.loadEventFeedsGroups();
    }

    componentDidUpdate(prevProps) {
        if (prevProps.activePage !== this.props.activePage
            || prevProps.sizePerPage !== this.props.sizePerPage) {
            this.loadEventFeedsGroups()
        }
    }

    loadEventFeedsGroups() {
        const { eventId, activePage, sizePerPage } = this.props;
        this.setState({loading: true})
        apiClient.getEventFeedGroups(eventId, activePage-1, sizePerPage).then(json => {
            this.setState({feedGroups: json.feed_groups, totalItemsCount: json.total_count});
        }).then(
            () => this.setState({loading: false})
        )
    }

    handleFiltersSubmit = filters => {
        this.props.resetActivePage();
        this.setState({filters})
    }

    render() {
        return (
            <div className="sub">
                <div className="container-fluid">
                    <div className="search-results-header">
                        <div className="text">
                            <h2>Feeds for event {this.props.eventId}</h2>
                        </div>
                    </div>
                    {
                        this.state.feedGroups.length > 0
                            ? <Fragment>
                                <EventFeedGroupsTable
                                    feedGroups={this.state.feedGroups}
                                    loading={this.state.loading}
                                />
                                {this.props.renderPagination(this.state.totalItemsCount)}
                            </Fragment>
                            : !this.state.loading
                                ? <div className="text" style={{textAlign: "center", marginTop: "100px"}}>
                                    <h2>There are no feeds associated with this event</h2>
                                </div>
                                : <Loading style={{marginTop: "100px"}} />
                    }

                </div>
            </div>
        );
    }
}

export default EventsLog;
