import React from 'react'
import {
    Route,
    Redirect,
    Switch
} from 'react-router-dom'

import Layout from './shared/Layout'

import Header from './shared/views/Header'
import MenuLinks from './customization/Header/MenuLinks'
import CustomStructure from './customization/Structure/Structure'
import Home from './shared/views/Home'
import Login from './shared/views/Login'
import FeedsList from './shared/views/FeedsList'
import EventsLog from './shared/views/EventsLog'
import EventFeedGroups from './shared/views/EventFeedGroups'
import PrivateRoute from './shared/PrivateRoute'
import Dashboard from './shared/views/Dashboard'

import SettingsForm from './customization/Settings/SettingsForm'
import { eventsTypesMapping } from './customization/EventsLog/eventsTypes'
import BatchActionsButton from './customization/BatchActions/BatchActionsButton'
import CustomDataSourceLabel from './customization/DataSourceLabel/DataSourceLabel'
import ViewRules from './shared/Scheduler'

function CustomDashboard(props) {
    return <Dashboard SettingsForm={SettingsForm} {...props} />
}

function CustomEventsLog(props) {
    return <EventsLog eventsTypesMapping={eventsTypesMapping} {...props} />
}

function CustomFeedsList(props) {
    return <FeedsList BatchActionsButton={BatchActionsButton} DataSourceLabel={CustomDataSourceLabel} {...props} />
}

function CustomHeader() {
    return <Header MenuLinks={MenuLinks} />
}


export default function App() {
    return (
        <Layout Header={CustomHeader}>
            <Switch>
                <Route exact path="/login" component={Login} />
                <PrivateRoute exact path="/" component={Home} />
                <PrivateRoute path="/structure" component={CustomStructure} />
                <PrivateRoute path="/feeds" component={CustomFeedsList} />
                <PrivateRoute path="/events" component={CustomEventsLog} />
                <PrivateRoute path="/event/:eventId" component={EventFeedGroups} />
                <PrivateRoute path="/view-rules" component={ViewRules} />
                <PrivateRoute path="/dashboard" component={CustomDashboard} />
                <Redirect from="*" to="/" />
            </Switch>
        </Layout>
    )
}
