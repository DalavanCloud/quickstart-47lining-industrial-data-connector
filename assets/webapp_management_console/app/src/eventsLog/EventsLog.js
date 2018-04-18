import React, { Component } from 'react'
import { connect } from 'react-redux'
import Loading from '../app/Loading.js'
import { toast } from 'react-toastify'

import { setNumberOfRecentEvents, setRecentEvents } from './EventsLogActions.js'
import { formatTimestamp } from '../utils.js'

import StatusLabel from '../common/StatusLabel.js'

import Client from '../ApiClient.js'


const defaultAttributes = [
    'update_timestamp',
    'event_type',
    'status'
]


class EventsTable extends Component {

    displayNamesMap = {
        'sync_pi_points': 'sync feeds',
        'sync_af': 'sync structure',
        'pi_points': 'feeds'
    }

    getDisplayName(label) {
        if (label in this.displayNamesMap) {
            return this.displayNamesMap[label];
        }
        return label;
    }

    attributesFormatter(event) {
        let attributes = [];
        for (let [key, val] of Object.entries(event)) {
            if (defaultAttributes.indexOf(key) === -1) {
                if (Array.isArray(val))
                    val = val.join(', ')
                if (val) {
                    attributes.push(<li key={key}><label>{this.getDisplayName(key)}:</label> {val}</li>)
                }
            }
        }
        return (
            <ul>
                {attributes}
            </ul>
        )
    }

    renderRow(event) {
        return (
            <tr key={event.update_timestamp}>
                <td>{formatTimestamp(event.update_timestamp)}</td>
                <td>{this.getDisplayName(event.event_type)}</td>
                <td>{this.attributesFormatter(event)}</td>
                <td><StatusLabel status={event.status} /></td>
            </tr>
        )
    }

    render() {
        return (
            <div className={`table-holder ${this.props.loading ? 'inactive' : ''}`}>
                <table className="checkbox-table">
                    <tbody>
                        <tr>
                            <th>Timestamp</th>
                            <th>Type</th>
                            <th>Attributes</th>
                            <th>Status</th>
                        </tr>
                        {
                            this.props.events.map(event => (
                                this.renderRow(event)
                            ))
                        }
                    </tbody>
                </table>
            </div>
        )
    }
}


class EventsLog extends Component {

    constructor(props) {
        super(props)
        this.state = {
            loading: true
        }
    }

    loadRecentEvents(number, notify=false) {
        this.setState({loading: true})
        Client.getRecentEvents(number).then(events => {
            this.props.setRecentEvents(events);
            notify && toast.info('Events log refreshed');
        }).then(
            () => this.setState({loading: false})
        ).catch(err => console.log(err))
    }

    componentDidMount() {
        this.loadRecentEvents(this.props.numberOfRecentEvents)
    }

    onChangeNumberOfEvents(event) {
        const number = event.target.value;
        this.loadRecentEvents(number);
        this.props.setNumberOfRecentEvents(number);
    }

    handleRefreshClick(event) {
        event.preventDefault();
        this.setState({loading: true});
        this.loadRecentEvents(this.props.numberOfRecentEvents, true);
    }

    render() {
        return (
            <div className="sub">
                <div className="container-fluid">
                    <div className="search-results-header">
                        <div className="text">
                            <h2>Events log</h2>
                        </div>
                        <div className="buttons">
                            <span>Show last</span>
                            <div className="form-group select">
                                <select
                                    className="form-control"
                                    id="show-last"
                                    value={this.props.numberOfRecentEvents}
                                    onChange={e => this.onChangeNumberOfEvents(e)}
                                >
                                    <option>10</option>
                                    <option>20</option>
                                    <option>30</option>
                                    <option>40</option>
                                    <option>50</option>
                                </select>
                            </div>
                            <span>events</span>
                            <button
                                className="btn btn-basic"
                                onClick={e => this.handleRefreshClick(e)}
                            >
                                <i className="fa fa-refresh"></i> Refresh events log
                            </button>
                        </div>
                    </div>
                    {
                        this.props.recentEvents.length === 0
                            ? <Loading />
                            : <EventsTable
                                events={this.props.recentEvents}
                                loading={this.state.loading}
                            />
                    }
                </div>
            </div>
        );
    }
}


const mapStateToProps = state => {
    return {
        recentEvents: state.recentEvents,
        numberOfRecentEvents: state.numberOfRecentEvents
    }
}

const mapDispatchToProps = dispatch => {
    return {
        setNumberOfRecentEvents: (number) => {
            dispatch(setNumberOfRecentEvents(number));
        },
        setRecentEvents: (number) => {
            dispatch(setRecentEvents(number));
        }
    }
}

const ConnectedEventsLog = connect(
    mapStateToProps,
    mapDispatchToProps
)(EventsLog)

export default ConnectedEventsLog
