import React, { Component } from 'react'
import { connect } from 'react-redux'
import Client from '../ApiClient.js'
import { toast } from 'react-toastify'

import { isLoggedIn } from './LoginActions.js'

import logo from '../resources/images/Logo_color.png'


class Login extends Component {

    constructor(props) {
        super(props);
        this.state = {
            username: '',
            password: ''
        }
    }

    handleSubmit(event) {
        event.preventDefault();
        Client.login(this.state.username, this.state.password).then(json => {
            if (json.loggedIn) {
                this.setState({loggedIn: true});
                this.props.dispatch(isLoggedIn(true));
                this.props.history.push('/');
            } else {
                this.props.dispatch(isLoggedIn(false));
                toast.warning('Invalid username or password')
                this.setState({username: '', password: ''});
            }
        }).catch(err => console.log(err));
    }

    render() {
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
