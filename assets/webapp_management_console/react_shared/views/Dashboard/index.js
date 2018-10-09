import React from 'react'

import Settings from '../Settings'
import UserManagement from '../UserManagement'


function Dashboard({ SettingsForm }) {
    return (
        <div className="scheduler">
            <div className="container-fluid">
                <div className="content">
                    <div className="form-box">
                        <Settings SettingsForm={SettingsForm} />
                    </div>
                    <div className="form-box">
                        <UserManagement />
                    </div>
                </div>
            </div>
        </div>
    );
}

Dashboard.defaultProps = {
    SettingsForm: undefined
}

export default Dashboard;
