import React, { Component, Fragment } from 'react'
import { toast } from 'react-toastify'

import Loading from '../../../components/Loading'
import apiClient from '../../../apiClient'

import UsersList from '../components/UsersList'
import OwnUsername from '../components/OwnUsername'


export default class UsersListContainer extends Component {

    constructor(props) {
        super(props)
        this.state = {
            users: [],
            ownUsername: '',
            loading: false
        }
    }

    componentDidMount() {
        this.setState({ loading: true });
        const username = sessionStorage.getItem('username');
        apiClient.listUsers().then(json => {
            this.setState({ users: json, ownUsername: username, loading: false });
        });
    }

    deleteUserHandler = username => {
        apiClient.deleteUser(username).then(() => {
            toast.info(`User ${username} deleted`)
        }).then(() => this.setState({
            users: this.state.users.filter(user => user.username !== username)
        }));
    }

    addUserHandler = (username, firstName, lastName, password) => {
        return apiClient.registerUser(username, firstName, lastName, password).then(
            () => {
                toast.info(`User ${username} added`);
            }
        ).then(() => this.setState({
            users: [
                ...this.state.users,
                {
                    username,
                    first_name: firstName,
                    last_name: lastName
                }
            ]
        }))
    }

    editUserHandler = (username, firstName, lastName) => {
        return apiClient.editUser(username, firstName, lastName).then(
            () => {
                toast.info(`User ${username} modified`);
            }
        ).then(() => this.setState({
            users: this.state.users.map(user =>
                user.username !== username
                    ? user
                    : {
                        username,
                        first_name: firstName,
                        last_name: lastName
                    }
            )
        }))
    }

    render() {
        return this.state.loading
            ? <Loading style={{marginTop: "100px"}} />
            : <Fragment>
                <OwnUsername username={this.state.ownUsername} />
                <UsersList
                    ownUsername={this.state.ownUsername}
                    users={this.state.users}
                    deleteUserHandler={this.deleteUserHandler}
                    addUserHandler={this.addUserHandler}
                    editUserHandler={this.editUserHandler}
                />
            </Fragment>
    }

}
