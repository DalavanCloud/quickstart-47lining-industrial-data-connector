import React, { Component } from 'react'
import {
    Col, FormGroup, ControlLabel, FormControl
} from 'react-bootstrap'


export default class Query extends Component {

    static validator(query) {
        if (query.length > 0)
            return 'success'
        return null
    }

    render() {
        return (
            <FormGroup
                controlId="query"
                className={this.props.className}
                validationState={this.constructor.validator(this.props.query)}
            >
                <Col componentClass={ControlLabel} sm={2}>
                    Query
                </Col>
                <Col sm={10}>
                    <FormControl
                        type="text"
                        value={this.props.query}
                        onChange={(event) => this.props.onChange(event)}
                    />
                </Col>
            </FormGroup>
        )
    }
}
