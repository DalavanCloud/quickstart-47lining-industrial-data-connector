import React, { Component } from 'react'

import {
    BrowserRouter as Router,
    Route,
    Redirect,
    Switch
} from 'react-router-dom'

import Header from '../header/Header.js'
import Structure from '../Structure'
import Home from '../home/Home.js'
import Login from '../login/Login.js'

import Modal from './Modal.js'
import FeedsList from '../FeedsList'
import EventsLog from '../eventsLog/EventsLog.js'
import PrivateRoute from '../login/PrivateRoute.js'
import ViewRules from '../scheduler/ViewRules.js'
import Settings from '../settings/Settings.js'
import { ToastContainer } from 'react-toastify';


class App extends Component {
    render() {
        return (
            <Router>
                <div>
                    <Header />
                    <Modal />
                    <ToastContainer autoClose={8000} pauseOnHover />
                    <Switch>
                        <Route exact path="/login" component={Login} />
                        <PrivateRoute exact path="/" component={Home} />
                        <PrivateRoute path="/structure" component={Structure} />
                        <PrivateRoute path="/feeds" component={FeedsList} />
                        <PrivateRoute path="/events" component={EventsLog} />
                        <PrivateRoute path="/view-rules" component={ViewRules} />
                        <PrivateRoute path="/settings" component={Settings} />
                        <Redirect from="*" to="/" />
                    </Switch>
                </div>
            </Router>
        );
    }
}

export default App;
