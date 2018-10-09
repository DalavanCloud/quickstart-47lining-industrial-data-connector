import React, { Component } from 'react'
import {
    Col, FormGroup, FormControl, ControlLabel,
    InputGroup, DropdownButton, MenuItem
} from 'react-bootstrap'


export class Interval extends Component {

    static validator(interval) {
        if (isNaN(Number(interval))) return 'error';
        else if (interval === '') return null;
        return 'success';
    }


    render() {
        return (
            <FormGroup
                controlId="intervalInput"
            >
                <Col componentClass={ControlLabel} sm={2}>
                    Interval
                </Col>
                <Col sm={10}>
                    <InputGroup>
                        <FormControl
                            type="text"
                            value={this.props.interval}
                            name="interval"
                            onChange={this.props.onChange}
                        />
                        <DropdownButton
                            componentClass={InputGroup.Button}
                            bsStyle="default"
                            title={this.props.intervalUnit}
                            onSelect={eventKey => this.props.setFieldValue('intervalUnit', eventKey)}
                            id="interval-unit-dropdown"
                        >
                            <MenuItem eventKey="seconds">seconds</MenuItem>
                            <MenuItem eventKey="minutes">minutes</MenuItem>
                            <MenuItem eventKey="hours">hours</MenuItem>
                        </DropdownButton>
                    </InputGroup>
                </Col>
            </FormGroup>
        )
    }
}

export default Interval
