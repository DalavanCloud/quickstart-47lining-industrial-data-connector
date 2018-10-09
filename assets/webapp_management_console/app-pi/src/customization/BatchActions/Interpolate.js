import React, { Component } from 'react'
import pluralize from 'pluralize'
import { Formik } from 'formik'
import { Button, Form, Col, FormGroup, FormControl, ControlLabel } from 'react-bootstrap'
import _ from 'lodash'

import apiClient from '../../apiClient'
import { getPayloadFromProps, getDefaultEventName } from '../../shared/BatchActions/utils'

import QueryOrDatepickers from '../../shared/BatchActions/components/QueryOrDatepickers'
import Interval from '../../shared/BatchActions/components/Interval'


class Interpolate extends Component {

    render() {
        const { feeds } = this.props;
        const totalCount = feeds ? feeds.length : this.props.feedsTotalCount;
        return (
            <div>
                <p>You are going to interpolate {totalCount} {pluralize('feed', totalCount)}</p>
                {totalCount > 100 && <p>This operation can take a long time!</p>}
                <hr />
                <Formik
                    initialValues={{
                        name: '',
                        syntax: false,
                        to: '',
                        from: '',
                        query: '',
                        interval: '',
                        interval_unit: 'seconds'
                    }}
                    validate={values => {
                        let errors = {};
                        if (!((values.syntax && values.query !== '') || (!values.syntax && values.to !== '' && values.from !== ''))) {
                            errors.syntax = 'Query or from and to required'
                        }
                        if (values.interval === '') {
                            errors.interval = 'Required'
                        }
                        return errors;
                    }}
                    onSubmit={
                        values => {
                            let payload = {...getPayloadFromProps(this.props), ...values}
                            apiClient.interpolateFeeds(payload);
                            this.props.closeModalCallback();
                        }
                    }
                    render={props => (
                        <Form
                            onSubmit={props.handleSubmit}
                            horizontal
                        >
                            <FormGroup>
                                <Col componentClass={ControlLabel} sm={2}>
                                    Name
                                </Col>
                                <Col sm={10}>
                                    <FormControl
                                        type="text"
                                        name="name"
                                        value={props.values.name}
                                        placeholder={getDefaultEventName('interpolate')}
                                        onChange={props.handleChange}
                                    />
                                </Col>
                            </FormGroup>
                            <QueryOrDatepickers
                                syntax={props.values.syntax}
                                to={props.values.to}
                                from={props.values.from}
                                query={props.values.query}
                                setFieldValue={props.setFieldValue}
                                onChange={props.handleChange}
                            />
                            <Interval
                                interval={props.values.interval}
                                intervalUnit={props.values.interval_unit}
                                setFieldValue={props.setFieldValue}
                                onChange={props.handleChange}
                            />
                            <Button
                                bsStyle="primary"
                                onClick={props.handleSubmit}
                                disabled={!_.isEmpty(props.errors) || !props.dirty}
                            >
                                Continue
                            </Button>
                        </Form>
                    )}
                />
            </div>
        )
    }
}

export default Interpolate;
