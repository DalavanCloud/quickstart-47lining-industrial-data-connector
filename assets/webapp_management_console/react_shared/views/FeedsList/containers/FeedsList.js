import React, { Component, Fragment } from 'react'
import { Set, console } from 'global'
import apiClient from '../../../apiClient'
import Loading from '../../../components/Loading'
import { connect } from 'react-redux'

import Table from '../components/Table'
import Header from '../components/Header'
import FilterBox from './FilterBox'
import SyncButton from './SyncButton'
import { reloadFeedList } from '../actions'


class FeedsList extends Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedIds: [],
            loading: true,
            feeds: [],
            feedsTotalCount: 0,
            subscribedCount: 0,
            unsubscribedCount: 0,
            pendingCount: 0,
            filters: {
                searchForStatus: 'all',
                searchPattern: '',
                useRegex: false
            }
        }
    }

    componentDidMount() {
        this.loadFeeds();
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevProps.activePage !== this.props.activePage
            || prevProps.sizePerPage !== this.props.sizePerPage
            || prevState.filters !== this.state.filters
            || (prevProps.shouldReloadFeedList !== this.props.shouldReloadFeedList && this.props.shouldReloadFeedList)) {
            this.loadFeeds()
        }
    }

    loadFeeds() {
        const { searchForStatus, searchPattern, useRegex } = this.state.filters;
        const { activePage, sizePerPage } = this.props;

        this.setState({
            selectedIds: [],
            loading: true
        });

        return apiClient.searchFeedsList(activePage-1, sizePerPage, searchForStatus, searchPattern, useRegex).then(response => {
            this.setState({
                selectedIds: Array(response.feeds.length).fill(false),
                feeds: response.feeds,
                feedsTotalCount: response.total_count,
                subscribedCount: response.subscribed_count,
                unsubscribedCount: response.unsubscribed_count,
                pendingCount: response.pending_count
            })
        }).then(
            () => {
                this.setState({loading: false});
                this.props.reloadFeedList(false);
            }
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

    handleFeedsFiltersSubmit = (searchForStatus, query, useRegex) => {
        this.props.resetActivePage();
        this.setState({
            filters: {
                searchPattern: query,
                searchForStatus,
                useRegex
            }
        });
    }

    getSelectedFeeds = () => {
        const { feeds, selectedIds } = this.state;

        if (feeds) {
            return Array.from(new Set(feeds.filter(
                (attr, id) => selectedIds[id]
            ).map(attr => attr.name)));
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
                            onSubmit={this.handleFeedsFiltersSubmit}
                        />
                        {this.state.feeds.length > 0
                            ? <Fragment>
                                <Header
                                    BatchActionsButton={this.props.BatchActionsButton}
                                    totalCount={this.state.feedsTotalCount}
                                    subscribedCount={this.state.subscribedCount}
                                    unsubscribedCount={this.state.unsubscribedCount}
                                    pendingCount={this.state.pendingCount}
                                    getSelectedFeeds={this.getSelectedFeeds}
                                    searchFilters={this.state.filters}
                                    disableSelectedFeedsActions={!this.state.selectedIds.reduce((prev, curr) => prev || curr, false)}
                                />
                                <Table
                                    rows={this.state.feeds}
                                    loading={this.state.loading}
                                    isSelectAll={this.isSelectAll()}
                                    handleToggle={this.handleToggle}
                                    handleToggleAll={this.handleToggleAll}
                                    selectedIds={this.state.selectedIds}
                                    DataSourceLabel={this.props.DataSourceLabel}
                                />
                                {this.props.renderPagination(this.state.feedsTotalCount)}
                            </Fragment>
                            : !this.state.loading
                                ? <div className="text" style={{textAlign: "center", marginTop: "100px"}}>
                                    <h2>There are no feeds matching your query</h2>
                                    <SyncButton style={{display: "inline-block", marginTop: "20px"}}/>
                                </div>
                                : <Loading style={{marginTop: "100px"}} />}
                    </Fragment>
                </div>
            </div>
        )
    }
}

const mapStateToProps = state => {
    return {
        shouldReloadFeedList: state.shouldReloadFeedList
    }
}

const mapDispatchToProps = dispatch => {
    return {
        reloadFeedList: (shouldReload) => {
            dispatch(reloadFeedList(shouldReload));
        }
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(FeedsList);