import React, { Fragment } from 'react'
import { PageHeader } from 'react-bootstrap'

import UsersList from './containers/UsersList'


function UserManagement() {
    return (
        <Fragment>
            <PageHeader style={{textAlign: "center"}}>Users</PageHeader>
            <UsersList />
        </Fragment>
    );
}

export default UserManagement;
