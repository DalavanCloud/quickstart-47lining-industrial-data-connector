import React from 'react'

import { ResetFiltersIcon } from '../../common/icons.js'

import Filter from './Filter.js'


export default function SearchBox({ filters, renderAddFilterForm, handleResetFilters, handleDeleteFilter }) {
    return (
        <div className="search main-search">
            <div className="item">
                <label>Search</label>
                <div className="inner">
                    {filters && filters.map((filter, i) => (
                        <Filter
                            key={i}
                            filter={filter}
                            onDelete={() => handleDeleteFilter(i)}
                        />
                    ))}
                    {filters && filters.length > 0 && <button
                        className="reset-filters"
                        onClick={() => handleResetFilters()}
                    >
                        <ResetFiltersIcon />
                    </button>}
                </div>
            </div>
            {renderAddFilterForm()}
        </div>
    )
}
