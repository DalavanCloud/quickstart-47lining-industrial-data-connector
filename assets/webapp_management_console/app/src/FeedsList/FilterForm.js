import React from 'react'

import Checkbox from '../common/Checkbox.js'
import DelayedTooltip from '../common/DelayedTooltip.js'
import { MagnifyingGlassIcon } from '../common/icons.js'


export default function FilterForm({
    values,
    handleChange,
    handleSubmit
}) {
    return (
        <form onSubmit={handleSubmit}>
            <div className="item">
                <label>Search</label>
            </div>
            <div className="item">
                <div className="inner">
                    <label>Status</label>
                    <div className="form-group select">
                        <select
                            className="form-control"
                            id="searchForStatus"
                            value={values.searchForStatus}
                            onChange={handleChange}
                        >
                            <option value="all">all</option>
                            <option value="subscribed">subscribed</option>
                            <option value="unsubscribed">unsubscribed</option>
                            <option value="pending">pending</option>
                        </select>
                    </div>
                </div>
                <div className="inner">
                    <DelayedTooltip
                        id="FeedsSearchTooltip"
                        tooltip="You can use wildcard *, e.g. prefix*001"
                    >
                        <input
                            placeholder="Search for..."
                            type="text"
                            id="query"
                            value={values.query}
                            onChange={handleChange}
                        />
                    </DelayedTooltip>
                    <Checkbox
                        id="useRegex"
                        checked={values.useRegex}
                        onChange={handleChange}
                    />
                    <label htmlFor="useRegex">Use regex</label>
                    <button type="submit" className="btn btn-primary">
                        <MagnifyingGlassIcon /> Filter feeds
                    </button>
                </div>
            </div>
        </form>
    )
}
