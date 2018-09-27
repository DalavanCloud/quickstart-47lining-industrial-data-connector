import React, { Component, Fragment } from 'react'
import UltimatePagination from 'react-ultimate-pagination-bootstrap-4'

import SearchResultsHeader from '../components/SearchResultsHeader'
import Asset from './Asset'


export default class SearchResults extends Component {

    constructor(props) {
        super(props);

        this.state = {
            open: Array(this.props.searchResults.assets.length).fill(false)
        }
    }

    componentWillReceiveProps(newProps) {
        if (newProps.searchResults.timestamp !== this.props.searchResults.timestamp) {
            this.setState({open: Array(newProps.searchResults.assets.length).fill(false)})
        }
    }

    handleAssetToggle = id => {
        let open = [...this.state.open];
        open[id] = !open[id]
        this.setState({open})
    }

    handleOpenAll = () => {
        this.setState({open: Array(this.props.searchResults.assets.length).fill(true)})
    }

    handleCloseAll = () => {
        this.setState({open: Array(this.props.searchResults.assets.length).fill(false)})
    }

    render() {
        const { searchResults, selectAsset, selectedAsset, searchFilters, activePage, sizePerPage, onPageChange, loading, attributesHeaders, createRowFromAttribute, BatchActionsButton, createAssetBasicInfo, apiClient } = this.props;
        const { open } = this.state;
        const totalPages = Math.ceil(searchResults.total_count / sizePerPage)

        return (
            <Fragment>
                <SearchResultsHeader
                    totalCount={searchResults.total_count}
                    feedsTotalCount={searchResults.feeds_total_count}
                    handleOpenAll={this.handleOpenAll}
                    handleCloseAll={this.handleCloseAll}
                    filters={searchFilters}
                    BatchActionsButton={BatchActionsButton}
                />
                {searchResults.assets.length > 0
                    ? <Fragment>
                        <div
                            className={`panel-group ${loading ? 'inactive' : ''}`}
                            id="accordion"
                            role="tablist"
                            aria-multiselectable="true"
                        >
                            {searchResults.assets.map((asset, id) => (<Asset
                                key={`${asset.id}-${searchResults.timestamp}`}
                                asset={asset}
                                active={asset.id === selectedAsset}
                                handleSelect={id => selectAsset(id)}
                                handleToggle={() => this.handleAssetToggle(id)}
                                open={open[id]}
                                filters={searchFilters.filter(filter => filter.type === 'attribute')}
                                attributesHeaders={attributesHeaders}
                                createRowFromAttribute={createRowFromAttribute}
                                BatchActionsButton={BatchActionsButton}
                                createAssetBasicInfo={createAssetBasicInfo}
                                apiClient={apiClient}
                            />))}
                        </div>
                        <nav aria-label="..." style={{marginTop: "30px"}}>
                            <UltimatePagination
                                currentPage={activePage > totalPages ? 1 : activePage}
                                totalPages={totalPages}
                                onChange={page => onPageChange(page)}
                            />
                        </nav>
                    </Fragment>
                    : <div className="text" style={{textAlign: "center"}}>
                        <h2>There are no assets matching selected filters</h2>
                    </div>}
            </Fragment>
        )
    }
}
