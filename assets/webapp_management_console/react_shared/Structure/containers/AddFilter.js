import React, {Component} from 'react'
import {Formik} from 'formik'

import AddFilterForm from '../components/AddFilterForm.js'


class AddFilter extends Component {

    render() {
        const { assetAttributes, feedAttributes } = this.props;

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
                render={ props =>
                    <AddFilterForm
                        assetAttributes={assetAttributes}
                        feedAttributes={feedAttributes}
                        {...props}
                    />
                }
            />
        )
    }
}

export default AddFilter;
