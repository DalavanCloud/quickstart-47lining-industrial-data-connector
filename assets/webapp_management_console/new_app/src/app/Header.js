import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Navbar, Nav, NavItem, NavDropdown, MenuItem, Glyphicon, Popover, OverlayTrigger } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import { LinkContainer } from 'react-router-bootstrap'
import Client from '../ApiClient.js'
import { withRouter } from 'react-router-dom'

import { isLoggedIn } from '../login/LoginActions.js'

import logo from './images/PI_AWS_ConnectorV2.png'

import './Header.css';

class Header extends Component {

    componentDidMount() {
        Client.checkIfLoggedIn().then(json => (
            this.props.dispatch(isLoggedIn(json.loggedIn))
        ))
    }

    handleLogoutButton() {
        Client.logout().then(() => {
            this.props.dispatch(isLoggedIn(false));
            this.props.history.push('/login');
        });
    }

    renderMenuForLoggedIn() {
        return [
            <Nav key={1}>
                <LinkContainer key={1} to="/af-structure">
                    <NavItem eventKey={1}>AF structure</NavItem>
                </LinkContainer>
                <LinkContainer key={2} to="/pi-points">
                    <NavItem eventKey={2}>PI Points</NavItem>
                </LinkContainer>
                <LinkContainer key={3} to="/events">
                    <NavItem eventKey={3}>Events log</NavItem>
                </LinkContainer>
            </Nav>,
            <AthenaLink key={2} />,
            <Nav key={3} pullRight>
                <NavDropdown
                    eventKey={1}
                    title={<Glyphicon glyph="user" />}
                    id="basic-nav-dropdown"
                >
                    <MenuItem
                        eventKey={1.1}
                        onSelect={() => this.handleLogoutButton()}
                    >
                        <Glyphicon glyph="off" /> Log out
                    </MenuItem>
                </NavDropdown>
            </Nav>
        ]
    }

    renderMenuForNotLoggedIn() {
        return (
            <Nav pullRight>
                <LinkContainer to="/login">
                    <NavItem eventKey={1}>Log in</NavItem>
                </LinkContainer>
            </Nav>
        )
    }

    render() {
        return (
            <Navbar collapseOnSelect>
                <Navbar.Header>
                    <Link to="/">
                        <img className="navbar-brand" src={logo} alt="PI2AWS connector" />
                    </Link>
                    <Navbar.Toggle />
                </Navbar.Header>
                <Navbar.Collapse>
                    {this.props.isLoggedIn ?
                        this.renderMenuForLoggedIn() : this.renderMenuForNotLoggedIn()}
                </Navbar.Collapse>
            </Navbar>
        );
    }
}

class AthenaLink extends Component {
    constructor(props) {
        super(props);
        this.state = {
            athenaDatabase: "",
            athenaTableName: "",
            athenaUrl: ""
        }
    }

    componentDidMount() {
        Client.getAthenaInfo().then(json => (
            this.setState({
                athenaDatabase: json.athena_database,
                athenaTableName: json.athena_table_name,
                athenaUrl: json.athena_url
            })
        )).catch(err => console.log(err));
    }

    render() {
        const helpPopover = (
            <Popover id="popover-trigger-click" title="Amazon Athena">
                In order to explore your data select <strong>{this.state.athenaDatabase}</strong> database and then <strong>{this.state.athenaTableName}</strong> table.
            </Popover>
        )
        return (
            <OverlayTrigger trigger={['hover', 'focus']} placement="bottom" overlay={helpPopover}>
                <Navbar.Text>
                    <Navbar.Link className="athena-link" href={this.state.athenaUrl} target="_blank">Explore data</Navbar.Link>
                </Navbar.Text>
            </OverlayTrigger>
        )
    }
}

const mapStateToProps = state => {
    return {
        isLoggedIn: state.isLoggedIn
    }
}

export default withRouter(connect(mapStateToProps)(Header));
