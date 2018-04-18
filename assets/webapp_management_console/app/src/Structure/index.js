import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { Date } from 'global'
import qs from 'qs'
import _ from 'lodash'
import { toast } from 'react-toastify'

import { selectAsset, setQueryString } from './actions'

import Client from '../ApiClient.js'

import AssetTree from './containers/AssetTree.js'

import SearchBox from './components/SearchBox.js'
import AddFilter from './containers/AddFilter.js'
import SearchResults from './containers/SearchResults.js'

import Loading from '../app/Loading.js'


class Structure extends Component {

    constructor(props) {
        super(props);

        this.state = {
            searchResults: undefined,
            pageSize: 5,
            loading: false
        }
    }

    componentDidMount() {
        let queryString = qs.parse(this.props.location.search.substr(1));
        if (_.isEmpty(queryString) && this.props.structureQueryString !== '') {
            this.props.history.push(`/structure/?${this.props.structureQueryString}`)
        } else {
            this.updateQueryString(queryString , {})
            this.search(queryString)
        }
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.location.search !== this.props.location.search) {
            let queryString = qs.parse(nextProps.location.search.substr(1));
            this.props.setQueryString(nextProps.location.search.substr(1));
            this.search(queryString)
        }
    }

    search(queryString) {
        const { pageSize } = this.state;
        this.setState({loading: true})
        const page = queryString.page ? queryString.page : 1;
        Client.searchAssets(queryString.searchFilters, page, pageSize).then(
            json => this.setState({
                searchResults: {...json, timestamp: new Date()},
                loading: false
            }),
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
        Client.syncStructure().then(() => {
            toast.info("Structure sync request sent");
        }).catch(err => console.error(err))
    }

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

    render() {
        const queryString = qs.parse(this.props.location.search.substr(1));
        const { searchFilters, page } = queryString;
        return (
            <div className="main">
                <div className="container-fluid">
                    <div className="left-panel">
                        <button className="btn btn-basic" onClick={this.handleStructureSync}>
                            Request Structure sync
                        </button>
                        <div className="side-menu">
                            <AssetTree
                                onAssetSelect={this.selectAsset}
                                selectedAsset={this.props.selectedAsset}
                            />
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
                            />
                            : <Loading timeout={1000} style={{marginTop: "100px"}} />}
                    </div>
                </div>
            </div>
        );
    }

}

const mapStateToProps = state => {
    return {
        selectedAsset: state.selectedAsset,
        structureQueryString: state.structureQueryString
    }
}

const mapDispatchToProps = dispatch => {
    return {
        selectAsset: asset => {
            dispatch(selectAsset(asset))
        },
        setQueryString: queryString => {
            dispatch(setQueryString(queryString))
        }
    }
}

const ConnectedStructure = connect(
    mapStateToProps,
    mapDispatchToProps
)(Structure)

export default withRouter(ConnectedStructure);
