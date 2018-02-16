import React, { Component } from 'react'
import { Form } from 'react-bootstrap'
import moment from 'moment'

import Loading from '../app/Loading.js'

import SubmitButton from './components/SubmitButton.js'

import Client from '../ApiClient.js'


class BaseForm extends Component {

    componentDidMount() {
        this.loadFormState()
    }

    loadFormState() {
        let newState = {...this.initialState};
        if(this.props.ruleName !== undefined) {
            Client.getRule(this.props.ruleName).then(json => {
                newState.form = {...newState.form, ...json};
                newState.disabledName = true;
                newState.loading = false;
                this.setState(newState)
            }).catch(err => console.log(err))
        } else {
            this.setState({loading: false})
        }
    }

    handleOnChange(event, attribute, valueOrChecked = 'value') {
        this.changeFormState(attribute, event.target[valueOrChecked]);
    }

    changeFormState(attribute, value) {
        let newState = {...this.state};
        newState.form[attribute] = value
        this.setState(newState);
    }

    handleSubmit(event, url, actionName) {
        event.preventDefault();

        let form = {...this.state.form};
        form = this.formatDatetime(form);

        let successMessage = `${actionName} request successfuly sent`;
        let failureMessage = `${actionName} request failed`;

        Client.sendForm(url, form, successMessage, failureMessage).then(
           () => {
               let newState = {...this.initialState}
               newState.loading = false;
               newState.disabledName = false;
               this.setState(newState)
           }
        );
        if (this.props.onSubmitCallback !== undefined)
            this.props.onSubmitCallback();

        if (this.props.formSubmitCustomCallback !== undefined)
            this.props.formSubmitCustomCallback();
    }

    formatDatetime(form) {
        if (form.from instanceof moment)
            form['from'] = form.from.format('YYYY-MM-DDTHH:mm:ss');
        if (form.to instanceof moment)
            form['to'] = form.to.format('YYYY-MM-DDTHH:mm:ss');
        return form;
    }

    setValidation(key, value) {
        let newState = {...this.state};
        newState.validation[key] = value
        this.setState(newState);
    }

    renderForm(title, url) {
        return (
            <Form
                onSubmit={(event) => this.handleSubmit(event, url, title)}
                horizontal
            >

                {this.state.loading ? <Loading />
                : this.renderFormComponents()}

                {!this.state.loading ?
                    <SubmitButton
                        label="Send"
                        disabled={!this.validate()}
                    /> : ''}
            </Form>
        )
    }
}

export default BaseForm
