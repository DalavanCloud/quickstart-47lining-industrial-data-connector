import React from 'react'
import {
    Col, Button, FormGroup
} from 'react-bootstrap'


export default function SubmitButton(props) {
    return (
        <FormGroup
            controlId="SubmitButton"
        >
            <Col smOffset={2} sm={10}>
                <Button {...props} type="submit" disabled={props.disabled}>
                    {props.label}
                </Button>
            </Col>
        </FormGroup>
    )
}
