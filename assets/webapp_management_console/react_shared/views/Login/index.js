import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Redirect } from "react-router-dom"
import apiClient from '../../apiClient'
import { toast } from 'react-toastify'

import { setIsLoggedIn } from './actions'

import logo from '../../resources/images/Logo_color.png'


class Login extends Component {

    constructor(props) {
        super(props);
        this.state = {
            username: '',
            password: '',
            redirectToReferrer: false
        }
    }

    handleSubmit(event) {
        event.preventDefault();
        apiClient.login(this.state.username, this.state.password).then(json => {
            if (json.id_token && json.access_token && json.refresh_token && json.username) {
                sessionStorage.setItem('id_token', json.id_token);
                sessionStorage.setItem('access_token', json.access_token);
                sessionStorage.setItem('refresh_token', json.refresh_token);
                sessionStorage.setItem('username', json.username);
                this.props.dispatch(setIsLoggedIn(true));
                this.setState({loggedIn: true, redirectToReferrer: true});
            } else {
                this.props.dispatch(setIsLoggedIn(false));
                toast.warning('Invalid username or password')
                this.setState({username: '', password: ''});
            }
        }).catch(err => console.log(err));
    }

    render() {
        const { from } = this.props.location.state || { from: { pathname: "/" } };
        const { redirectToReferrer } = this.state;

        if (redirectToReferrer) {
            return <Redirect to={from} />;
        }

        return (
            <div className="login">
                <div className="form-box">
                    <div className="text-center branding">
                        <img style={{width: '390px'}} src={logo} alt="logo" />
                    </div>
                    <form
                        className="form-content"
                        onSubmit={(e) => this.handleSubmit(e)}
                    >
                        <div className="input-holder">
                            <input
                                type="text"
                                className="form-control"
                                placeholder="Username"
                                value={this.state.username}
                                onChange={(event) => this.setState({username: event.target.value})}
                                required
                                autoFocus
                            />
                        </div>
                        <div className="input-holder">
                            <input
                                type="password"
                                className="form-control"
                                placeholder="Password"
                                value={this.state.password}
                                onChange={(event) => this.setState({password: event.target.value})}
                                required
                            />
                        </div>
                        <button
                            className="btn btn-primary"
                            type="submit"
                            onClick={(e) => this.handleSubmit(e)}
                        >
                            Login
                        </button>
                    </form>
                </div>
            </div>
        );
    }
}

const ConnectedLogin = connect()(Login)

export default ConnectedLogin;
