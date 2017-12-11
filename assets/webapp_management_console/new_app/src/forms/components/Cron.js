import React, { Component } from 'react'
import {
    Col, FormGroup, FormControl, ControlLabel
} from 'react-bootstrap'

import cronstrue from 'cronstrue'


function cronToString(cron) {
    // cronstrue is nice, but it doesn't handle AWS specific cron expressions
    // properly
    let parts = cron.split(' ');

    let errorMsg = 'invalid cron';

    if (parts.length !== 6) {
        throw new Error(errorMsg);
    } else if (parts[5] === '') {
        throw new Error(errorMsg);
    } else if (parts[5] !== '*' && isNaN(Number(parts[5]))) {
        throw new Error(errorMsg);
    } else if (!((parts[2] === '?') ^ (parts[4] === '?'))) { //!XOR
        throw new Error(errorMsg);
    } else if ((parts[5] > 1970 && parts[5] < 2200) || parts[5] === '*') {
        if (parts[5] === '*') {
            // dirty hack
            // if parts[5] === '*', cronstrue thinks that it is a cron expression
            // with second
            // AWs-specific cron parser is needed
            parts[5] = '1970';
            return cronstrue.toString(parts.join(' ')).replace(', only in 1970', '');
        }
        return cronstrue.toString(cron);
    } else {
        throw new Error(errorMsg);
    }
}

export class Cron extends Component {

    static validator(cron) {
        if (cron === '') return null;

        try {
            cronToString(cron);
            return 'success';
        } catch(err) {
            return 'error';
        }
    }

    renderCronDescription(cron) {
        return (
            <p>
                {cronToString(cron)}
            </p>
        )
    }

    render() {
        const validationState = this.constructor.validator(this.props.cron);
        return (
            <FormGroup
                controlId="cron"
                validationState={validationState}
            >
                <Col componentClass={ControlLabel} sm={2}>
                    Cron
                </Col>
                <Col sm={10}>
                    <FormControl
                        type="text"
                        value={this.props.cron}
                        onChange={(event) => this.props.onChange(event, 'cron')}
                    />
                    {validationState === 'success' ? this.renderCronDescription(this.props.cron) : ''}
                </Col>

            </FormGroup>
        )
    }
}

export default Cron
