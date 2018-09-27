import React, { Fragment } from 'react'

import UserRow from './UserRow'

import AddUserButton from '../containers/AddUserButton'


export default function UsersList({ users, ownUsername, deleteUserHandler, addUserHandler, editUserHandler }) {
    return (
        <Fragment>
            <table className="checkbox-table">
                <tbody>
                    <tr>
                        <th>Username</th>
                        <th>Full name</th>
                        <th>Actions</th>
                    </tr>
                    {users.map(user => <UserRow
                        key={user.username}
                        isLoggedIn={user.username === ownUsername}
                        user={user}
                        deleteUserHandler={deleteUserHandler}
                        editUserHandler={editUserHandler}
                    />)}
                </tbody>
            </table>
            <AddUserButton
                addUserHandler={addUserHandler}
            />
        </Fragment>
    );
}
