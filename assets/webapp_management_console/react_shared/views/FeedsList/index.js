import React, { Component } from 'react'

import Paginated from '../../components/Paginated'
import FeedsList from './containers/FeedsList'

import BatchActionsButton from '../../BatchActions/BatchActionsButton'


export default class FeedsListContainer extends Component {
    render() {
        return (
            <Paginated
                render={({activePage, sizePerPage, renderPagination, resetActivePage}) => (
                    <FeedsList
                        BatchActionsButton={this.props.BatchActionsButton}
                        DataSourceLabel={this.props.DataSourceLabel}
                        activePage={activePage}
                        sizePerPage={sizePerPage}
                        renderPagination={renderPagination}
                        resetActivePage={resetActivePage}
                    />
                )}
            />
        )
    }
}

FeedsListContainer.defaultProps = {
    BatchActionsButton: BatchActionsButton
}
