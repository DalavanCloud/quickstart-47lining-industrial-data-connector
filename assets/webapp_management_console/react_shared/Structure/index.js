import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { Date } from 'global'
import qs from 'qs'
import _ from 'lodash'
import { toast } from 'react-toastify'
import { Button } from 'react-bootstrap'

import { showConfirmActionModal } from '../Modal/actions'

import { selectAsset, setQueryString } from './actions'

import SideMenu from '../components/SideMenu'

import SearchBox from './components/SearchBox'
import AddFilter from './containers/AddFilter'
import SearchResults from './containers/SearchResults'

import Loading from '../components/Loading'
import { reloadFeedList } from '../views/FeedsList/actions'

class Structure extends Component {

    constructor(props) {
        super(props);

        this.state = {
            searchResults: undefined,
            pageSize: 5,
            loading: false,
            reset: false,
        };
    }

    componentDidMount() {
        let queryString = qs.parse(this.props.location.search.substr(1));
        this.updateQueryString(queryString , {});
        this.search(queryString)
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.location.search !== this.props.location.search
            || (nextProps.shouldReloadFeedList !== this.props.shouldReloadFeedList && nextProps.shouldReloadFeedList)) {
            let queryString = qs.parse(nextProps.location.search.substr(1));
            this.props.setQueryString(nextProps.location.search.substr(1));
            this.search(queryString)
        }
    }

    search(queryString) {
        const { pageSize } = this.state;
        this.setState({loading: true})
        const page = queryString.page ? queryString.page : 1;
        this.props.apiClient.searchAssets(queryString.searchFilters, page, pageSize).then(
            json => {
                this.setState({
                    searchResults: {...json, timestamp: new Date()},
                    loading: false
                });
                this.props.reloadFeedList(false);
            },
            err => console.error(err)
        )
    }

    updateQueryString(newKeyValues, queryStringObj = null) {
        if (queryStringObj === null) {
            queryStringObj = qs.parse(this.props.location.search.substr(1));
        }
        queryStringObj = {...queryStringObj, ...newKeyValues};
        const queryString = qs.stringify(queryStringObj);
        this.props.setQueryString(queryString);
        this.props.history.push(`/structure/?${queryString}`);
    }

    setFilters(filters) {
        this.updateQueryString({searchFilters: filters, page: 1});
    }

    handleAddFilter = filter => {
        let queryString = qs.parse(this.props.location.search.substr(1));
        let filters = queryString.searchFilters || [];
        let existingFilterIndex = _.findIndex(filters, {type: filter.type, parameter: filter.parameter});
        if (existingFilterIndex > -1) {
            filters.splice(existingFilterIndex, 1);
        }
        filters.push(filter);
        this.setFilters(filters);
    }

    handleDeleteFilter = index => {
        let queryString = qs.parse(this.props.location.search.substr(1));
        let filters = queryString.searchFilters || [];
        filters.splice(index, 1);
        this.setFilters(filters);
    }

    handleResetFilters = () => {
        this.setFilters([]);
    }

    handleStructureSync = () => {
        this.props.apiClient.syncStructure().then(() => {
            toast.info("Structure sync request sent");
        }).catch(err => console.error(err))
    };

    handleStructureReset = additionalResettingActions => {
        const delay = 60000;
        const msgTemplate = `Resetting data will take about ${delay/1000+10} seconds but can increase depending on number on subscribed feeds. Wait, please.`;

        this.props.apiClient.resetAllData().then(() => {
            additionalResettingActions();
            toast.info(msgTemplate, { autoClose: delay });
        }).catch(err => console.error(err));
    };

    selectAsset = assetId => {
        this.handleAddFilter({
            type: 'asset',
            parameter: 'path',
            value: `${assetId}*`
        })
        this.props.selectAsset(assetId);
    }

    handleSearch = values => {
        this.updateQueryString({searchForm: values});
    }

    handlePageChange = page => {
        this.updateQueryString({page: page});
    }

    handleResetStructureConfirmation = () => {
        this.handleStructureReset(() => {
            this.setState({searchResults: {assets: []}, reset: true});
            this.props.history.push(`/structure`)
        })
    }

    render() {
        const queryString = qs.parse(this.props.location.search.substr(1));
        const { searchFilters, page } = queryString;
        const { attributesHeaders, assetAttributes, feedAttributes, createRowFromAttribute, BatchActionsButton, createAssetBasicInfo, apiClient } = this.props;
        return (
            <div className="main">
                <div className="container-fluid">
                    <div className="left-panel">
                        <Button className="btn btn-basic" onClick={this.handleStructureSync}>
                            Request Structure sync
                        </Button>
                        <Button
                            className="btn btn-danger"
                            style={{marginTop: "10px"}}
                            onClick={() => this.props.showConfirmActionModal({
                                title: "Reset data",
                                paragraphsWithDescription: [
                                    "You are going to reset all data. Structure and Feeds will be removed from application.",
                                    "Are you sure you want to perform this action?"
                                ],
                                confirmActionLabel: "Yes",
                                cancelActionLabel: "No",
                                confirmActionCallback: this.handleResetStructureConfirmation
                            })}
                        >
                            Reset Structure and Feeds
                        </Button>
                        <div className="side-menu">
                            {this.state.reset
                                ? null :
                                <SideMenu
                                    getNodeChildren={apiClient.getAssetChildren}
                                    onNodeSelect={this.selectAsset}
                                    selectedNode={this.props.selectedAsset}
                                />}
                        </div>
                    </div>
                    <div className="main-content">
                        <SearchBox
                            filters={searchFilters}
                            handleDeleteFilter={this.handleDeleteFilter}
                            handleResetFilters={this.handleResetFilters}
                            renderAddFilterForm={() => (
                                <AddFilter
                                    handleAddFilter={this.handleAddFilter}
                                    assetAttributes={assetAttributes}
                                    feedAttributes={feedAttributes}
                                />
                            )}
                        />
                        {this.state.searchResults
                            ? <SearchResults
                                searchResults={this.state.searchResults}
                                selectedAsset={this.props.selectedAsset}
                                selectAsset={this.selectAsset}
                                searchFilters={searchFilters === undefined ? [] : searchFilters}
                                activePage={parseInt(page === undefined ? 1 : page, 10)}
                                sizePerPage={this.state.pageSize}
                                onPageChange={this.handlePageChange}
                                loading={this.state.loading}
                                attributesHeaders={attributesHeaders}
                                createRowFromAttribute={createRowFromAttribute}
                                BatchActionsButton={BatchActionsButton}
                                createAssetBasicInfo={createAssetBasicInfo}
                                apiClient={apiClient}
                            />
                            : <Loading style={{marginTop: "100px"}} />}
                    </div>
                </div>
            </div>
        );
    }

}

const mapStateToProps = state => {
    return {
        selectedAsset: state.selectedAsset,
        structureQueryString: state.structureQueryString,
        shouldReloadFeedList: state.shouldReloadFeedList
    }
};

const mapDispatchToProps = dispatch => {
    return {
        showConfirmActionModal: (...args) => {
            dispatch(showConfirmActionModal(...args))
        },
        selectAsset: asset => {
            dispatch(selectAsset(asset))
        },
        setQueryString: queryString => {
            dispatch(setQueryString(queryString))
        },
        reloadFeedList: (shouldReload) => {
            dispatch(reloadFeedList(shouldReload));
        }
    }
};

const ConnectedStructure = connect(
    mapStateToProps,
    mapDispatchToProps
)(Structure);

export default withRouter(ConnectedStructure);
