import React from 'react'
import { Button, Form, Col, FormGroup, FormControl, ControlLabel } from 'react-bootstrap'


export default function UserForm({ handleSubmit, handleChange, values }) {
    return (
        <Form
            onSubmit={handleSubmit}
            horizontal
        >
            <FormGroup>
                <Col componentClass={ControlLabel} sm={3}>
                    First name
                </Col>
                <Col sm={9}>
                    <FormControl
                        type="text"
                        name="firstName"
                        value={values.firstName}
                        onChange={handleChange}
                    />
                </Col>
            </FormGroup>
            <FormGroup>
                <Col componentClass={ControlLabel} sm={3}>
                    Last name
                </Col>
                <Col sm={9}>
                    <FormControl
                        type="text"
                        name="lastName"
                        value={values.lastName}
                        onChange={handleChange}
                    />
                </Col>
            </FormGroup>
            <Button
                bsStyle="primary"
                type="submit"
                onClick={handleSubmit}
            >
                Continue
            </Button>
        </Form>
    )
}
