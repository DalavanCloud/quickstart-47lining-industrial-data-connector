import React, { Fragment } from 'react'

import { MagnifyingGlassIcon } from '../../common/icons.js'


export default function AddFilterForm({
    values,
    handleChange,
    handleSubmit
}) {
    return (
        <form className="item" onSubmit={handleSubmit}>
            <div className="form-group select">
                <select
                    className="form-control"
                    id="type"
                    value={values.type}
                    onChange={handleChange}
                >
                    <option value="asset">Asset</option>
                    <option value="attribute">Attribute</option>
                </select>
            </div>
            <div className="form-group select">
                <select
                    className="form-control"
                    id="parameter"
                    value={values.parameter}
                    onChange={handleChange}
                >
                    {
                        values.type === 'asset'
                            ? <Fragment>
                                <option value="name">Name</option>
                                <option value="description">Description</option>
                                <option value="category">Category</option>
                                <option value="template">Template</option>
                                <option value="path">Path</option>
                            </Fragment>
                            : <Fragment>
                                <option value="name">Name</option>
                                <option value="description">Description</option>
                                <option value="category">Category</option>
                                <option value="point">Feed</option>
                            </Fragment>
                    }
                </select>
            </div>
            <div className="inner">
                <input
                    type="text"
                    id="value"
                    placeholder="Search for..."
                    value={values.value}
                    onChange={handleChange}
                />
                <button
                    type="submit"
                    className="btn btn-primary"
                    onClick={handleSubmit}
                >
                    <MagnifyingGlassIcon /> Add Search
                </button>
            </div>
        </form>
    )
}
