import React from 'react'
import PropTypes from 'prop-types'
import pluralize from 'pluralize'

import SyncButton from '../containers/SyncButton'


export default function Header({
    totalCount,
    subscribedCount,
    unsubscribedCount,
    pendingCount,
    getSelectedFeeds,
    searchFilters,
    disableSelectedFeedsActions,
    BatchActionsButton
}) {
    return (
        <div className="search-results-header">
            <div className="text">
                <h2>Search results</h2>
                <p>Found {totalCount} {pluralize('feed', totalCount)}: {subscribedCount}&nbsp;subscribed, {unsubscribedCount}&nbsp;unsubscribed and {pendingCount}&nbsp;pending</p>
            </div>
            <div className="buttons">
                <BatchActionsButton
                    getSelectedFeeds={getSelectedFeeds}
                    searchFilters={searchFilters}
                    feedsTotalCount={totalCount}
                    disableSelectedFeedsActions={disableSelectedFeedsActions}
                />
                <SyncButton />
            </div>
        </div>
    )
}

Header.propTypes = {
    totalCount: PropTypes.number,
    getSelectedFeeds: PropTypes.func,
    disableSelectedFeedsActions: PropTypes.bool,
    searchFilters: PropTypes.object
}
