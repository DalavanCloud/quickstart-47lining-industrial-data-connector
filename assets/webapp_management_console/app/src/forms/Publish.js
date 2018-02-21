import React from 'react'
import BaseForm from './BaseForm.js'
import { Col } from 'react-bootstrap'
import Datepicker from './components/Datepicker.js'

class Publish extends BaseForm {
    constructor(...args) {
        super(...args);
        this.state = {
            form: {
                from: '',
                to: ''
            }
        }
    }

    validate() {
        return Datepicker.validator(this.state.form.from) === 'success' & Datepicker.validator(this.state.form.to) === 'success'
    }

    render() {
        return this.renderForm(
            'Publish Managed Feeds',
            '/publish'
        )
    }

    renderFormComponents() {
        return [
            <Col sm={6} key="A">
                <Datepicker
                    label="From"
                    value={this.props.from}
                    onChange={(value) => this.changeFormState('from', value)}
                />
            </Col>,
            <Col sm={6} key="B">
                <Datepicker
                    label="To"
                    value={this.props.to}
                    onChange={(value) => this.changeFormState('to', value)}
                />
            </Col>
        ]
    }
}

export default Publish;
