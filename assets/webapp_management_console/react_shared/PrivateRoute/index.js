import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Redirect } from 'react-router-dom'

import { setIsLoggedIn } from '../views/Login/actions'


export class PrivateRoute extends Component {

    render() {
        if (this.props.isLoggedIn) {
            return <this.props.component {...this.props} />;
        } else {
            return <Redirect to={{
                pathname: '/login',
                state: { from: this.props.location }
            }} />;
        }
    }
}

const mapStateToProps = state => {
    return {
        isLoggedIn: state.isLoggedIn,
    }
}

const mapDispatchToProps = dispatch => {
    return {
        setIsLoggedIn: isLoggedIn => {
            dispatch(setIsLoggedIn(isLoggedIn));
        }
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(PrivateRoute)
