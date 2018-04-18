import React, { Component } from 'react';
import { Formik } from 'formik';
import { connect } from 'react-redux'
import _ from 'lodash'
import { setSettings } from '../actions.js'
import { toast } from 'react-toastify'

import Client from '../../ApiClient.js'

import SettingsForm from '../components/SettingsForm.js'


export class SettingFormContainer extends Component {

    render() {
        return (
            !_.isEmpty(this.props.settings) && <Formik
                initialValues={{
                    afDbName: this.props.settings.afDbName,
                    deploymentName: this.props.settings.deploymentName
                }}
                onSubmit={(
                    values,
                    { setSubmitting }
                ) => {
                    setSubmitting(true);
                    Client.saveSettings({settings: values}).then(
                        () => {
                            toast.success('Settings saved, now you can request sync of Structure and Feeds List', { autoClose: false })
                            this.props.setSettings(values);
                            setSubmitting(false);
                        },
                        err => {
                            setSubmitting(false);
                            console.error(err);
                        })
                }}
                render={SettingsForm}
            />
        )
    }
}

const mapStateToProps = state => {
    return {
        settings: state.settings
    }
}

const mapDispatchToProps = dispatch => {
    return {
        setSettings: settings => {
            dispatch(setSettings(settings));
        }
    }
}

const ConnectedSettingFormContainer = connect(
    mapStateToProps,
    mapDispatchToProps
)(SettingFormContainer)

export default ConnectedSettingFormContainer;
