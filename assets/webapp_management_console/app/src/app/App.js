import React, { Component } from 'react'

import {
    BrowserRouter as Router,
    Route,
    Redirect,
    Switch
} from 'react-router-dom'
import { Grid, Row } from 'react-bootstrap'

import Header from './Header.js'
import AfStructure from '../afStructure/AfStructure.js'
import Home from '../home/Home.js'
import ConnectedLogin from '../login/Login.js'

import './App.css'
import Notification from './Notification.js'
import ConnectedModal from './Modal.js'
import PipointsList from '../piPoints/PiPointsList.js'
import EventsLog from '../eventsLog/EventsLog.js'
import PrivateRoute from '../login/PrivateRoute.js'



class App extends Component {
    render() {
        return (
            <Router>
                <div className="App">
                    <Header showLogoutButton />
                    <Grid>
                        <Row>
                            <Notification />
                            <ConnectedModal />
                            <Switch>
                                <Route exact path="/login" component={ConnectedLogin} />
                                <PrivateRoute exact path="/" component={Home} />
                                <PrivateRoute path="/af-structure" component={AfStructure} />
                                <PrivateRoute path="/pi-points" component={PipointsList} />
                                <PrivateRoute path="/events" component={EventsLog} />
                                <Redirect from="*" to="/" />
                            </Switch>
                        </Row>
                    </Grid>
                </div>
            </Router>
        );
    }
}

export default App;
