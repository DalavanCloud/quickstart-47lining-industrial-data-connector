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
