import React from 'react'
import pluralize from 'pluralize'


export default function SearchResultsHeader({ totalCount, feedsTotalCount, filters, handleOpenAll, handleCloseAll, BatchActionsButton }) {
    return (
        <div className="search-results-header">
            <div className="text">
                <h2>Search results</h2>
                <p>
                    {`Found ${totalCount} ${pluralize('asset', totalCount)}
                     with ${feedsTotalCount} ${pluralize('feed', feedsTotalCount)}`}
                </p>
            </div>
            <div className="buttons">
                <BatchActionsButton
                    showSelectedFeedsActions={false}
                    filters={filters}
                    feedsTotalCount={feedsTotalCount}
                />
                <button
                    className="btn btn-secondary"
                    onClick={handleOpenAll}
                >
                    Open all
                </button>
                <button
                    className="btn btn-secondary"
                    onClick={handleCloseAll}
                >
                    Hide all
                </button>
            </div>
        </div>
    );
}
