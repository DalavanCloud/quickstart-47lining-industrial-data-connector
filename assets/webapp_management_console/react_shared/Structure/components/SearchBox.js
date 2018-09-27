import React from 'react'

import { ResetFiltersIcon } from '../../components/icons'

import Filter from './Filter'


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
