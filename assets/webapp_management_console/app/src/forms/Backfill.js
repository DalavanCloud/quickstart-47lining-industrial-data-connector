import React from 'react'

import BaseForm from './BaseForm.js'

import NonEmptyInput from './components/NonEmptyInput.js'
import ManagedFeedInput from './components/ManagedFeedInput.js'
import QueryOrDatepickers from './components/QueryOrDatepickers.js'

import { val2bool } from './utils.js'


class Backfill extends BaseForm {

    constructor(...args) {
        super(...args);
        this.state = {
            form : {
                feeds: this.props.points,
                allPoints: this.props.allPoints,
                syntax: false,
                query: '',
                from: '',
                to: '',
                name: ''
            }
        };
    }

    validate() {
        return val2bool(NonEmptyInput.validator(this.state.form.name)) &
               val2bool(ManagedFeedInput.validator(this.state.form)) &
               val2bool(QueryOrDatepickers.validator(this.state.form))
    }

    render() {
        return this.renderForm(
            'Request backfill',
            '/backfill'
        )
    }

    renderFormComponents() {
        return [
            <NonEmptyInput
                key="name"
                value={this.state.form.name}
                label="Name"
                attributeName="name"
                onChange={(...args) => this.changeFormState(...args)}
            />,
            <ManagedFeedInput
                key="ManagedFeedInput"
                feeds={this.state.form.feeds}
                allPoints={this.state.form.allPoints}
                multi
                onChange={(...args) => this.changeFormState(...args)}
                onCheckboxChange={(...args) => this.handleOnChange(...args)}
            />,
            <QueryOrDatepickers
                key="QueryOrDatepickers"
                {...this.state.form}
                onChange={(...args) => this.handleOnChange(...args)}
                onDatepickerChange={(...args) => this.changeFormState(...args)}
            />
        ];
    }
}

export default Backfill;
