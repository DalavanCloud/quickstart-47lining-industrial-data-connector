import React, { Component } from 'react'
import { Formik } from 'formik'

import FilterForm from '../components/FilterForm'


export default class FilterBox extends Component {

    render() {
        const {eventsTypesMapping} = this.props;
        return (
            <div className="search pi-search">
                <Formik
                    key="filter-feeds-form"
                    initialValues={{
                        type: 'all',
                        status: 'all',
                        from: '',
                        to: ''
                    }}
                    onSubmit={
                        values => this.props.onSubmit(values)
                    }
                    render={props => <FilterForm eventsTypesMapping={eventsTypesMapping} {...props} />}
                />
            </div>
        )

    }
}
