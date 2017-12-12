import React, { Component } from 'react'
import {
    Col, FormGroup, FormControl, ControlLabel
} from 'react-bootstrap'


export class NonEmptyInput extends Component {

    static validator(value, integer = false) {
        if (integer) {
            if (isNaN(Number(value))) return 'error';
        }
        if (value === '') return null;
        return 'success';
    }

    render() {
        return (
            <FormGroup
                controlId="nonEmptyInput"
                validationState={this.constructor.validator(this.props.value, this.props.integer)}
            >
                <Col componentClass={ControlLabel} sm={2}>
                    {this.props.label}
                </Col>
                <Col sm={10}>
                    <FormControl
                        type="text"
                        value={this.props.value}
                        onChange={(event) => this.props.onChange(this.props.attributeName, event.target.value)}
                        disabled={this.props.disabled}
                    />
                </Col>
            </FormGroup>
        )
    }
}

export default NonEmptyInput
