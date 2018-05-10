import React, { Fragment } from 'react'


export default function Checkbox({ id, checked, onChange }) {
    return (
        <Fragment>
            <input
                type="checkbox"
                id={`checkbox-${id}`}
                name={id}
                checked={checked}
                onChange={onChange}
            />
            <label htmlFor={`checkbox-${id}`}><span className="custom-checkbox"></span></label>
        </Fragment>
    )
}
