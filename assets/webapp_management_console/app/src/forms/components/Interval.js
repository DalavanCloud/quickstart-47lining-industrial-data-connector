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
                validationState={this.constructor.validator(this.props.interval)}
            >
                <Col componentClass={ControlLabel} sm={2}>
                    Interval
                </Col>
                <Col sm={10}>
                    <InputGroup>
                        <FormControl
                            type="text"
                            value={this.props.interval}
                            onChange={(event) => this.props.onChange(event, 'interval')}
                            help="wrong"
                        />
                        <DropdownButton
                            componentClass={InputGroup.Button}
                            id="input-dropdown-addon"
                            title={this.props.intervalUnit}
                            onSelect={(eventKey, event) => this.props.changeFormState('intervalUnit', eventKey)}
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
