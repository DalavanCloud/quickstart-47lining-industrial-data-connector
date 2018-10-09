import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import { withRouter } from 'react-router-dom'

import apiClient from '../../apiClient'
import { setIsLoggedIn } from '../Login/actions'
import Menu from './Menu'
import company47logo from '../../resources/images/logo.jpg'
import logo from '../../resources/images/Logo.png'
import MenuLinks from './MenuLinks'


import './Header.css'

class Header extends Component {

    componentWillMount() {
        let accessToken = sessionStorage.getItem('access_token');
        let idToken = sessionStorage.getItem('id_token');
        let refreshToken = sessionStorage.getItem('refresh_token');
        let username = sessionStorage.getItem('username');
        if (accessToken && idToken && refreshToken && username) {
            this.props.dispatch(setIsLoggedIn(true));
        } else {
            this.props.dispatch(setIsLoggedIn(false));
        }
    }

    handleLogoutButton() {
        apiClient.logout().then(() => {
            sessionStorage.removeItem('access_token');
            sessionStorage.removeItem('refresh_token');
            sessionStorage.removeItem('id_token');
            sessionStorage.removeItem('username');
            this.props.dispatch(setIsLoggedIn(false));
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
                            MenuLinks={this.props.MenuLinks}
                            handleLogoutButton={() => this.handleLogoutButton()}
                        />}
                </div>
            </div>
        )
    }
}

Header.defaultProps = {
    MenuLinks: MenuLinks
}

const mapStateToProps = state => {
    return {
        isLoggedIn: state.isLoggedIn
    }
}

export default withRouter(connect(mapStateToProps)(Header));
