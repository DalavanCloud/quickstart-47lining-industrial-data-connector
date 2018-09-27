import React, { Component } from 'react'
import { Formik } from 'formik'

import UserForm, { initialValues } from '../components/AddUserForm'


export default class AddUserModal extends Component {

    render() {
        const { addUserHandler, closeModalCallback } = this.props;
        return (
            <div>
                <Formik
                    initialValues={initialValues}
                    onSubmit={
                        ({ username, firstName, lastName, password }) =>
                            addUserHandler(username, firstName, lastName, password).then(
                                () => closeModalCallback()
                            )
                    }
                    render={props => <UserForm {...props} />}
                />
            </div>
        )
    }
}
