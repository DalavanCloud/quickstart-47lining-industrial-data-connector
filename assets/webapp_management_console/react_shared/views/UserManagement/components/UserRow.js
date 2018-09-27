import React from 'react'

import DeleteUserButton from '../containers/DeleteUserButton'
import EditUserButton from '../containers/EditUserButton'


export default function UserRow({ user, deleteUserHandler, editUserHandler, isLoggedIn }) {
    return (
        <tr className={isLoggedIn ? 'highlighted' : ''}>
            <td>{user.username}</td>
            <td>{`${user.first_name ? user.first_name : ''} ${user.last_name ? user.last_name : ''}`}</td>
            <td style={{whiteSpace: "nowrap"}}>
                <EditUserButton
                    username={user.username}
                    firstName={user.first_name}
                    lastName={user.last_name}
                    editUserHandler={editUserHandler}
                />&nbsp;
                {!isLoggedIn && <DeleteUserButton
                    username={user.username}
                    deleteUserHandler={() => deleteUserHandler(user.username)}
                />}
            </td>
        </tr>
    )
}
