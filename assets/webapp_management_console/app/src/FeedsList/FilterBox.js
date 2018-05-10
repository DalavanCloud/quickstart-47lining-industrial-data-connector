import React, { Component } from 'react';
import { Formik } from 'formik'

import FilterForm from './FilterForm'


export default class FilterBox extends Component {

    render() {
        return (
            <div className="search pi-search">
                <Formik
                    key="filter-feeds-form"
                    initialValues={{
                        searchForStatus: 'all',
                        query: '',
                        useRegex: false

                    }}
                    onSubmit={
                        values => {
                            const { searchForStatus, query, useRegex } = values;
                            this.props.onSubmit(searchForStatus, query, useRegex)
                        }
                    }
                    render={FilterForm}
                />
            </div>
        )

    }
}
