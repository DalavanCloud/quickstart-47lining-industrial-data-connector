import React, { Component, Fragment } from 'react'
import { Set, console } from 'global'
import Client from '../ApiClient'
import { connect } from 'react-redux'
import { showModal } from '../app/actions'
import Loading from '../app/Loading'

import Table from './Table'
import Header from './Header'
import FilterBox from './FilterBox'
import SyncButton from './SyncButton'


class FeedsList extends Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedIds: [],
            loading: true,
            activePage: 1,
            sizePerPage: 10,
            feeds: [],
            feedsTotalCount: 0,
            searchForStatus: 'all',
            searchPattern: '',
            useRegex: false
        }
    }

    componentDidMount() {
        this.loadfeeds();
    }

    loadfeeds(activePage = this.state.activePage, sizePerPage = this.state.sizePerPage,
        searchForStatus = this.state.searchForStatus, searchPattern = this.state.searchPattern,
        useRegex = this.state.useRegex) {

        this.setState({
            selectedIds: [],
            loading: true
        });

        const status = searchForStatus === 'all' ? undefined : searchForStatus;

        Client.searchFeedsList(activePage-1, sizePerPage, status, searchPattern, useRegex).then(response => {
            this.setState({
                selectedIds: Array(response.pi_points.length).fill(false),
                feeds: response.pi_points,
                feedsTotalCount: response.total_count
            })
        }).then(
            () => this.setState({loading: false})
        ).catch(err => console.error(err));
    }

    isSelectAll() {
        return this.state.selectedIds.reduce((prev, curr) => prev && curr, true)
    }

    handleToggle = index => {
        let selectedIds = [...this.state.selectedIds]
        selectedIds[index] = !selectedIds[index]
        this.setState({selectedIds})
    }

    handleToggleAll = () => {
        this.setState({selectedIds: Array(this.state.feeds.length).fill(!this.isSelectAll())})
    }

    onPageChange(page, sizePerPage = undefined) {
        this.setState({selectAll: false, activePage: page, sizePerPage: sizePerPage || this.state.sizePerPage});
        this.loadfeeds(page);
    }

    onSizePerPageChange(sizePerPage) {
        const maxPageNumber = Math.ceil(this.state.feedsTotalCount / sizePerPage);
        const activePage = this.state.activePage > maxPageNumber ? maxPageNumber : this.state.activePage;
        this.setState({sizePerPage, activePage});
        this.loadfeeds(activePage, sizePerPage);
    }

    handlefeedsFiltersSubmit = (searchForStatus, query, useRegex) => {
        this.setState({searchPattern: query, searchForStatus, useRegex, activePage: 1});
        this.loadfeeds(1, undefined, searchForStatus, query, useRegex);
    }

    getSelectedFeeds = () => {
        const { feeds, selectedIds } = this.state;

        if (feeds) {
            return Array.from(new Set(feeds.filter(
                (attr, id) => selectedIds[id]
            ).map(attr => attr.pi_point)));
        } else {
            return [];
        }
    }

    render() {
        return (
            <div className="sub">
                <div className="container-fluid">
                    <Fragment>
                        <FilterBox
                            onSubmit={this.handlefeedsFiltersSubmit}
                        />
                        {this.state.feeds.length > 0
                            ? <Fragment>
                                <Header
                                    totalCount={this.state.feedsTotalCount}
                                    getSelectedFeeds={this.getSelectedFeeds}
                                    searchForStatus={this.state.searchForStatus}
                                    searchPattern={this.state.searchPattern}
                                    disableSelectedFeedsActions={!this.state.selectedIds.reduce((prev, curr) => prev || curr, false)}
                                />
                                <Table
                                    rows={this.state.feeds}
                                    activePage={this.state.activePage}
                                    itemsCountPerPage={this.state.sizePerPage}
                                    totalItemsCount={this.state.feedsTotalCount}
                                    onChange={page => this.onPageChange(page)}
                                    handleToggle={this.handleToggle}
                                    selectedIds={this.state.selectedIds}
                                    isSelectAll={this.isSelectAll()}
                                    handleToggleAll={this.handleToggleAll}
                                    sizePerPage={this.state.sizePerPage}
                                    onSizePerPageChange={sizePerPage => this.onSizePerPageChange(sizePerPage)}
                                    loading={this.state.loading}
                                />
                            </Fragment>
                            : !this.state.loading
                                ? <div className="text" style={{textAlign: "center", marginTop: "100px"}}>
                                    <h2>There are no feeds matching your query</h2>
                                    <SyncButton style={{display: "inline-block", marginTop: "20px"}}/>
                                </div>
                                : <Loading timeout={1000} style={{marginTop: "100px"}} />}
                    </Fragment>
                </div>
            </div>
        )
    }
}

const mapDispatchToProps = dispatch => {
    return {
        showModal: (title, modalComponent, props) => {
            dispatch(showModal(title, modalComponent, props));
        }
    }
}

export default connect(
    undefined,
    mapDispatchToProps
)(FeedsList)
