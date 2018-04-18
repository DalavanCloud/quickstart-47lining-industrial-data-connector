import React from 'react';
import { PageHeader } from 'react-bootstrap';

import Form from './containers/SettingsFormContainer.js'


function Settings() {
    return (
        <div className="sub">
            <div className="form-box">
                <PageHeader style={{textAlign: "center"}}>Settings</PageHeader>
                <Form />
            </div>
        </div>
    );
}

export default Settings;
