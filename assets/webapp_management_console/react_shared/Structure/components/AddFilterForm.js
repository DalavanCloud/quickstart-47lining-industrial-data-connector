import React, { Fragment } from 'react'

import { MagnifyingGlassIcon } from '../../components/icons'


export default function AddFilterForm({
    values,
    handleChange,
    handleSubmit,
    assetAttributes,
    feedAttributes
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
                                {
                                    Object.keys(assetAttributes).map(attr =>
                                        <option value={attr}>{assetAttributes[attr]}</option>
                                    )
                                }
                            </Fragment>
                            : <Fragment>
                                {
                                    Object.keys(feedAttributes).map(attr =>
                                        <option value={attr}>{feedAttributes[attr]}</option>
                                    )
                                }
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
