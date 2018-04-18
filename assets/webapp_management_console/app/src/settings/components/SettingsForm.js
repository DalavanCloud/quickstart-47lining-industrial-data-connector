import React from 'react';
import { FormGroup, ControlLabel, Button } from 'react-bootstrap';



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
                    name="afDbName"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.afDbName}
                />
                <ControlLabel>Deployment name:</ControlLabel>
                <input
                    className="form-control"
                    type="text"
                    name="deploymentName"
                    onChange={handleChange}
                    onBlur={handleBlur}
                    value={values.deploymentName}
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
