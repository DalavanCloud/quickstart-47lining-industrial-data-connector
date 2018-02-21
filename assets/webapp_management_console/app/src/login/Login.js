import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Form, FormGroup, Grid, Col, FormControl, Button, ControlLabel } from 'react-bootstrap'
import Client from '../ApiClient.js'

import { addNotification } from '../app/actions.js'
import { isLoggedIn } from './LoginActions.js'


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
                this.props.dispatch(addNotification('Invalid username or password', 'danger'));
                this.setState({username: '', password: ''});
            }
        }).catch(err => console.log(err));
    }

    renderLoginForm() {
        return (
            <Form onSubmit={(e) => this.handleSubmit(e)} horizontal>
                <FormGroup controlId="formHorizontalUsername">
                    <Col componentClass={ControlLabel} sm={2}>
                        Username
                    </Col>
                    <Col sm={10}>
                        <FormControl type="text" value={this.state.username} onChange={(event) => this.setState({username: event.target.value})} placeholder="Username" />
                    </Col>
                </FormGroup>

                <FormGroup controlId="formHorizontalPassword">
                    <Col componentClass={ControlLabel} sm={2}>
                        Password
                    </Col>
                    <Col sm={10}>
                        <FormControl type="password" value={this.state.password} onChange={(event) => this.setState({password: event.target.value})} placeholder="Password" />
                    </Col>
                </FormGroup>

                <FormGroup>
                    <Col smOffset={2} sm={10}>
                        <Button type="submit" onClick={(e) => this.handleSubmit(e)}>
                            Log in
                        </Button>
                    </Col>
                </FormGroup>
            </Form>
        );
    }

    render() {
        return (
            <Grid style={{ textAlign: "left" }}>
                <Col md={2} />
                <Col md={8}>
                    <h3 id="pi-tag-name" className="page-header">Login</h3>
                    {this.renderLoginForm()}
                </Col>
                <Col md={2} />
            </Grid>
        );
    }

}

const ConnectedLogin = connect()(Login)

export default ConnectedLogin;
