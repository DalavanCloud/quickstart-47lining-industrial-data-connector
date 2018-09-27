import React, { Component } from 'react'
import { Formik } from 'formik'

import UserForm from '../components/EditUserForm'


export default class EditUserModal extends Component {

    render() {
        const { editUserHandler, closeModalCallback, username, firstName, lastName } = this.props;
        return (
            <div>
                <Formik
                    initialValues={{
                        firstName,
                        lastName
                    }}
                    onSubmit={
                        ({ firstName, lastName }) => {
                            editUserHandler(username, firstName, lastName).then(
                                () => closeModalCallback()
                            )
                        }
                    }
                    render={props => <UserForm {...props} />}
                />
            </div>
        )
    }
}
