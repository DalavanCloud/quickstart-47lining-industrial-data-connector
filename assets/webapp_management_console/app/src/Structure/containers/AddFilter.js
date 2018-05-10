import React, { Component } from 'react'
import { Formik } from 'formik'

import AddFilterForm from '../components/AddFilterForm.js'


class AddFilter extends Component {

    render() {
        return (
            <Formik
                key="search-form"
                initialValues={{
                    type: 'asset',
                    parameter: 'name',
                    value: ''

                }}
                onSubmit={
                    (values, { resetForm }) => {
                        this.props.handleAddFilter(values)
                        resetForm();
                    }
                }
                render={AddFilterForm}
            />
        )
    }
}

export default AddFilter;
