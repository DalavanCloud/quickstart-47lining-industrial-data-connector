import React from 'react'
import { Formik } from 'formik'
import Client from '../ApiClient.js'


export default function Scheduler({ cron, type }) {
    return (
        <Formik
            key="search-form"
            initialValues={{
                cron: cron
            }}
            onSubmit={
                (values, { setSubmitting }) => {
                    setSubmitting(true);
                    Client.setSchedulerRule(type, values.cron).then(
                        () => setSubmitting(false)
                    )
                }
            }
            render={({
                values,
                handleChange,
                handleSubmit,
                isSubmitting
            }) => (
                <form className="form-content" onSubmit={handleSubmit}>
                    <div className="form-group select">
                        <select
                            className="form-control"
                            name="cron"
                            value={values.cron}
                            onChange={handleChange}
                        >
                            <option value="0 0 * * ? 1970">Disabled</option>
                            <option value="0 0 * * ? *">Every 1 day</option>
                            <option value="0 0 1/7 * ? *">Every 1 week</option>
                            <option value="0 0 1/14 * ? *">Every 2 weeks</option>
                        </select>
                    </div>
                    <button
                        className="btn btn-primary"
                        type="submit"
                        disabled={isSubmitting}
                        onClick={handleSubmit}
                    >
                        {isSubmitting
                            ? <i className="fa fa-spinner fa-spin" aria-hidden="true"></i>
                            : <i className="fa fa-floppy-o" aria-hidden="true"></i> } Save
                    </button>
                </form>
            )}
        />
    )
}

Scheduler.defaultProps = {
    cron: "0 0 * * ? 1970",
    type: "af-structure"
}
