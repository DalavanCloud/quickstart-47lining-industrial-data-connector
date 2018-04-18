import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import Client from '../ApiClient.js'
import { withRouter } from 'react-router-dom'

import { isLoggedIn } from '../login/LoginActions.js'

import Menu from './Menu.js'

import company47logo from '../resources/images/logo.jpg'
import logo from '../resources/images/Logo.png'


import './Header.css';

class Header extends Component {

    componentDidMount() {
        Client.checkIfLoggedIn().then(json => {
            this.props.dispatch(isLoggedIn(json.loggedIn));
        })
    }

    handleLogoutButton() {
        Client.logout().then(() => {
            this.props.dispatch(isLoggedIn(false));
            this.props.history.push('/login');
        });
    }

    render() {
        return (
            <div className="top standard-top">
                <div className="main-menu">
                    <div className="branding">
                        <div className="logo">
                            <a href="http://www.47lining.com">
                                <img src={company47logo} alt="47-logo"/>
                            </a>
                        </div>
                        <div className="logo">
                            <Link to="/">
                                <img src={logo} alt="logo" />
                            </Link>
                        </div>
                    </div>
                    {this.props.isLoggedIn
                        && <Menu
                            handleLogoutButton={() => this.handleLogoutButton()}
                        />}
                </div>
            </div>
        )
    }
}


const mapStateToProps = state => {
    return {
        isLoggedIn: state.isLoggedIn
    }
}

export default withRouter(connect(mapStateToProps)(Header));
