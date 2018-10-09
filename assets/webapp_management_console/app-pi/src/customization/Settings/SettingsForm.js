import React from 'react'
import { FormGroup, ControlLabel, Button } from 'react-bootstrap'



export default function Form({
    values,
    handleChange,
    handleBlur,
    handleSubmit,
    isSubmitting,
}) {
    return (
        <form onSubmit={handleSubmit}>
            <FormGroup
                controlId="settings-form"
            >
                <ControlLabel>Structure Database name:</ControlLabel>
                <input
                    className="form-control"
                    type="text"
                    name="as_db_name"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.as_db_name}
                />
                <ControlLabel>Deployment name:</ControlLabel>
                <input
                    className="form-control"
                    type="text"
                    name="deployment_name"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.deployment_name}
                />
                <ControlLabel>Feed group size:</ControlLabel>
                <input
                    className="form-control"
                    type="text"
                    name="feed_group_size"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.feed_group_size}
                />
                <ControlLabel>Backfill/Interpolation request time window (in days):</ControlLabel>
                <input
                    className="form-control"
                    type="text"
                    name="time_window_days"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.time_window_days}
                />
            </FormGroup>
            <Button
                type="submit"
                disabled={isSubmitting}
                bsStyle="primary"
            >
                Save
            </Button>
        </form>
    )
}
