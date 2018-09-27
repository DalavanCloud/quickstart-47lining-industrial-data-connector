import React from 'react'
import { Button, Form, Col, FormGroup, FormControl, ControlLabel } from 'react-bootstrap'


export const initialValues = {
    username: '',
    firstName: '',
    lastName: '',
    password: ''
};


export default function UserForm({ handleSubmit, handleChange, values }) {
    return (
        <Form
            onSubmit={handleSubmit}
            horizontal
        >
            <FormGroup>
                <Col componentClass={ControlLabel} sm={3}>
                    Username
                </Col>
                <Col sm={9}>
                    <FormControl
                        type="text"
                        name="username"
                        value={values.username}
                        onChange={handleChange}
                    />
                </Col>
            </FormGroup>
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
            <FormGroup>
                <Col componentClass={ControlLabel} sm={3}>
                    Password
                </Col>
                <Col sm={9}>
                    <FormControl
                        type="password"
                        name="password"
                        value={values.password}
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
