import React from 'react'
import PropTypes from 'prop-types'
import pluralize from 'pluralize'

import SyncButton from './SyncButton'
import BatchActionsButton from '../BatchActions/BatchActionsButton.js'


export default function Header({ totalCount, getSelectedFeeds, searchForStatus, searchPattern, disableSelectedFeedsActions }) {
    return (
        <div className="search-results-header">
            <div className="text">
                <h2>Search results</h2>
                <p>Found {totalCount} {pluralize('feed', totalCount)}</p>
            </div>
            <div className="buttons">
                <BatchActionsButton
                    getSelectedFeeds={getSelectedFeeds}
                    searchForStatus={searchForStatus}
                    searchPattern={searchPattern}
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
    searchForStatus: PropTypes.string,
    searchPattern: PropTypes.string,
    disableSelectedFeedsActions: PropTypes.bool
}
