import React from 'react'
import { Formik } from 'formik'
import { connect } from 'react-redux'
import _ from 'lodash'
import { setSettings } from '../actions'
import { toast } from 'react-toastify'

import apiClient from '../../../apiClient'

import DefaultSettingsForm from '../components/SettingsForm'


export function SettingsFormContainer({ SettingsForm, settings, setSettings }) {
    return (
        !_.isEmpty(settings) && <Formik
            initialValues={{...settings}}
            onSubmit={(
                values,
                { setSubmitting }
            ) => {
                setSubmitting(true);
                apiClient.saveSettings(values).then(
                    () => {
                        toast.success('Settings saved')
                        setSettings(values);
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

SettingsFormContainer.defaultProps = {
    SettingsForm: DefaultSettingsForm
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

const ConnectedSettingsFormContainer = connect(
    mapStateToProps,
    mapDispatchToProps
)(SettingsFormContainer)

export default ConnectedSettingsFormContainer;
