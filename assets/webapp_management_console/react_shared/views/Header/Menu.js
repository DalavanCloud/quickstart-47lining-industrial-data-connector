import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { NavLink } from 'react-router-dom'

import { loadSettings } from '../Settings/actions'
import { SettingsIcon, LogOutIcon } from '../../components/icons'
import apiClient from '../../apiClient'


export class Menu extends Component {

    constructor(props) {
        super(props);
        this.state = {
            dataTransportService: '',
            connectorType: ''
        }
    }

    connectorTypeToHistorianMap = {
        'PI': 'OSISOFT',
        'KEPWARE': 'KEPWARE',
        'WONDERWARE': 'WONDERWARE'
    }

    componentDidMount() {
        this.props.loadSettings();
        apiClient.getAthenaInfo().then(json => (
            this.setState({
                dataTransportService: json.data_transport_service,
                connectorType: json.connector_type
            })
        )).catch(err => console.error(err));
    }

    render() {
        const { settings, handleLogoutButton, structureQueryString, MenuLinks } = this.props;
        return (
            <Fragment>
                <ul className="menu">
                    <MenuLinks structureQueryString={structureQueryString} />
                </ul>

                <div className="item deployment-name">
                    {settings.deployment_name &&
                    <Fragment><div>Deployment</div><div><strong>{settings.deployment_name}</strong></div></Fragment>}
                </div>
                <div className="item deployment-name" style={{marginLeft: '20px'}}>
                    <div>Historian:</div>
                    <div><strong>{this.connectorTypeToHistorianMap[this.state.connectorType]}</strong></div>
                    <div>Transport Service:</div>
                    <div><strong>{this.state.dataTransportService}</strong></div>
                </div>
                <div className="item buttons">
                    <NavLink component="button" to="/dashboard">
                        <SettingsIcon />
                    </NavLink>
                    <button onClick={() => handleLogoutButton()} type="button">
                        <LogOutIcon />
                    </button>
                </div>
            </Fragment>
        )
    }
}


const mapStateToProps = state => {
    return {
        settings: state.settings,
        structureQueryString: state.structureQueryString
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
