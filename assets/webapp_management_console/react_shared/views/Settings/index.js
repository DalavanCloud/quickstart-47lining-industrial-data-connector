import React, { Fragment } from 'react'
import { PageHeader } from 'react-bootstrap'

import Form from './containers/SettingsFormContainer'


function Settings({ SettingsForm }) {
    return (
        <Fragment>
            <PageHeader style={{textAlign: "center"}}>Settings</PageHeader>
            <Form SettingsForm={SettingsForm} />
        </Fragment>
    );
}

export default Settings;
