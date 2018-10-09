import React, { Component, Fragment } from 'react'

import Loading from '../../../components/Loading'
import apiClient from '../../../apiClient'

import EventsTable from '../components/EventsTable'
import FilterBox from './FilterBox'


class EventsLog extends Component {

    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            events: [],
            filters: {
                type: 'all',
                status: 'all',
                from: '',
                to: ''
            },
            totalItemsCount: 0
        }
    }

    componentDidMount() {
        this.loadEvents();
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevProps.activePage !== this.props.activePage
            || prevProps.sizePerPage !== this.props.sizePerPage
            || prevState.filters !== this.state.filters) {
            this.loadEvents()
        }
    }

    loadEvents() {
        const { type, status, from, to } = this.state.filters;
        const { activePage, sizePerPage } = this.props;
        this.setState({loading: true})
        apiClient.getEvents(type, status, from, to, activePage-1, sizePerPage).then(json => {
            this.setState({events: json.events, totalItemsCount: json.total_count});
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
                    <FilterBox
                        onSubmit={this.handleFiltersSubmit}
                        eventsTypesMapping={this.props.eventsTypesMapping}
                    />
                    <div className="search-results-header">
                        <div className="text">
                            <h2>Events log</h2>
                        </div>
                    </div>
                    {
                        this.state.events.length > 0
                            ? <Fragment>
                                <EventsTable
                                    eventsTypesMapping={this.props.eventsTypesMapping}
                                    events={this.state.events}
                                    loading={this.state.loading}
                                />
                                {this.props.renderPagination(this.state.totalItemsCount)}
                            </Fragment>
                            : !this.state.loading
                                ? <div className="text" style={{textAlign: "center", marginTop: "100px"}}>
                                    <h2>There are no events matching your query</h2>
                                </div>
                                : <Loading style={{marginTop: "100px"}} />
                    }

                </div>
            </div>
        );
    }
}

export default EventsLog;
