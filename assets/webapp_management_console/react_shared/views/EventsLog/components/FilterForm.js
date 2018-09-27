import React from 'react'
import Datetime from 'react-datetime'

import { MagnifyingGlassIcon } from '../../../components/icons'


export default function FilterForm({
    values,
    handleChange,
    handleSubmit,
    setFieldValue,
    eventsTypesMapping
}) {
    return (
        <form onSubmit={handleSubmit}>
            <div className="item">
                <label>Filter</label>
            </div>
            <div className="item">
                <div className="inner" style={{width: "100%"}}>
                    <label>Type</label>
                    <div className="form-group select">
                        <select
                            className="form-control"
                            name="type"
                            value={values.type}
                            onChange={handleChange}
                        >
                            <option value="all">all</option>
                            {
                                Object.entries(eventsTypesMapping).map(mapping => (
                                    <option key={`option-${mapping[0]}`} value={mapping[0]}>{mapping[1]}</option>
                                ))
                            }
                        </select>
                    </div>
                    <label>Status</label>
                    <div className="form-group select">
                        <select
                            className="form-control"
                            name="status"
                            value={values.status}
                            onChange={handleChange}
                        >
                            <option value="all">All</option>
                            <option value="success">Success</option>
                            <option value="failure">Failure</option>
                            <option value="pending">Pending</option>
                        </select>
                    </div>
                    <label>From</label>
                    <Datetime
                        className="rdt form-group select datetime-select"
                        style={{overflow: "visible"}}
                        value={values.from}
                        onChange={from => setFieldValue('from', from)}
                        inputProps={{className: "rdt-form-control"}}
                    />
                    <label>To</label>
                    <Datetime
                        className="rdt form-group select datetime-select"
                        style={{overflow: "visible"}}
                        value={values.to}
                        onChange={to => setFieldValue('to', to)}
                        inputProps={{className: "rdt-form-control"}}
                    />

                    <button type="submit" className="btn btn-primary">
                        <MagnifyingGlassIcon /> Filter events log
                    </button>
                </div>
            </div>
        </form>
    )
}
