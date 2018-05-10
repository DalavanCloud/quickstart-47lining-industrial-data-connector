import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { Popover, OverlayTrigger } from 'react-bootstrap'
import { NavLink } from 'react-router-dom'
import Client from '../ApiClient.js'

import { StructureIcon, FeedsIcon, EventsLogIcon, SchedulerIcon, AthenaIcon, SettingsIcon, LogOutIcon } from '../common/icons.js'

import MenuLink from './MenuLink.js'

import { loadSettings } from '../settings/actions.js'


export class Menu extends Component {

    componentDidMount() {
        this.props.loadSettings()
    }

    render() {
        return (
            <Fragment>
                <ul className="menu">
                    <MenuLink to="/structure">
                        <StructureIcon /> Structure
                    </MenuLink>
                    <MenuLink to="/feeds">
                        <FeedsIcon /> Feeds List
                    </MenuLink>
                    <MenuLink to="/events">
                        <EventsLogIcon /> Events log
                    </MenuLink>
                    <MenuLink to="/view-rules">
                        <SchedulerIcon /> Scheduler rules
                    </MenuLink>
                    <li className="item">
                        <AthenaLink />
                    </li>
                </ul>
                <div className="item deployment-name">
                    {this.props.settings.deploymentName &&
                    <Fragment><div>Deployment</div><div><strong>{this.props.settings.deploymentName}</strong></div></Fragment>}
                </div>
                <div className="item buttons">
                    <NavLink component="button" to="/settings">
                        <SettingsIcon />
                    </NavLink>
                    <button onClick={() => this.props.handleLogoutButton()} type="button">
                        <LogOutIcon />
                    </button>
                </div>
            </Fragment>
        )
    }
}

class AthenaLink extends Component {
    constructor(props) {
        super(props);
        this.state = {
            athenaDatabase: "",
            athenaNumericTableName: "",
            athenaTextTableName: "",
            athenaUrl: ""
        }
    }

    componentDidMount() {
        Client.getAthenaInfo().then(json => (
            this.setState({
                athenaDatabase: json.athena_database,
                athenaNumericTableName: json.athena_numeric_table_name,
                athenaTextTableName: json.athena_text_table_name,
                athenaUrl: json.athena_url
            })
        )).catch(err => console.log(err));
    }

    render() {
        const { athenaDatabase, athenaNumericTableName, athenaTextTableName, athenaUrl } = this.state;
        const helpPopover = (
            <Popover
                id="popover-trigger-click"
                title="Amazon Athena"
                style={{fontWeight: "100"}}
            >
                In order to explore your data select <strong>{athenaDatabase}</strong> database and then <strong>{athenaNumericTableName}</strong> or <strong>{athenaTextTableName}</strong> table.
            </Popover>
        )
        return (
            <OverlayTrigger trigger={['hover', 'focus']} placement="bottom" overlay={helpPopover}>
                <a href={athenaUrl}>
                    <AthenaIcon /> Explore data
                </a>
            </OverlayTrigger>
        )
    }
}

const mapStateToProps = state => {
    return {
        settings: state.settings
    }
}

const mapDispatchToProps = dispatch => {
    return {
        loadSettings: () => {
            dispatch(loadSettings());
        }
    }
}

export default withRouter(connect(
    mapStateToProps,
    mapDispatchToProps
)(Menu))
