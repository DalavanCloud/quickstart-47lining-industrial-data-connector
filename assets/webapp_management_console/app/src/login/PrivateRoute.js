import React, { Component } from 'react'
import Client from '../ApiClient.js'
import { Redirect } from 'react-router-dom'

import Loading from '../app/Loading.js'


export class PrivateRoute extends Component {

    constructor(props) {
        super(props);
        this.state = {
            isLoggedIn: false,
            loading: true
        }
    }

    componentDidMount() {
        this.setState({ isLoading: true });
        Client.checkIfLoggedIn().then(response => this.setState({isLoggedIn: response.loggedIn, loading: false}));
    }

    render() {
        if (this.state.loading) {
            return <Loading />
        }
        if (this.state.isLoggedIn) {
            return <this.props.component {...this.props} />;
        } else {
            return <Redirect to={{pathname: '/login'}} />;
        }
    }
}

export default PrivateRoute;
