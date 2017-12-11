import React, { Component } from 'react'
import { Label, PageHeader, Button, Grid, Row, Col, Form, FormControl, ControlLabel, Glyphicon } from 'react-bootstrap'
import { connect } from 'react-redux'
import { addNotification } from '../app/actions.js'
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table'
import 'react-bootstrap-table/dist/react-bootstrap-table.min.css'
import Loading from '../app/Loading.js'

import { setNumberOfRecentEventsDays, setRecentEvents } from './EventsLogActions.js'
import { formatTimestamp } from '../utils.js'

import Client from '../ApiClient.js'

import './EventsLog.css'


const statusToBsStyleMap = {
    success: 'success',
    failure: 'danger',
    pending: 'info'
}

const defaultAttributes = [
    'update_timestamp',
    'event_type',
    'status'
]

function statusFormatter(status, row) {
    return <Label bsStyle={statusToBsStyleMap[status]}>{status}</Label>
}

function attributesFormatter(_, row) {
    let attributes = [];
    for (let [key, val] of Object.entries(row)) {
        if (defaultAttributes.indexOf(key) === -1) {
            if (Array.isArray(val))
                val = val.join(', ')
            attributes.push(<li key={key}><strong>{key}:</strong> {val}</li>)
        }
    }
    return (
        <ul>
            {attributes}
        </ul>
    )
}

function EventsTable(props) {
    return (
        <BootstrapTable
            data={props.events}
            striped
            hover
        >
            <TableHeaderColumn
                width="20%"
                dataField="update_timestamp"
                isKey
                dataAlign="center"
                dataFormat={formatTimestamp}
                dataSort
            >
                Timestamp
            </TableHeaderColumn>
            <TableHeaderColumn
                width="15%"
                dataField="event_type"
                dataAlign="center"
                dataSort
            >
                Type
            </TableHeaderColumn>
            <TableHeaderColumn
                width="50%"
                dataFormat={attributesFormatter}
            >
                Attributes
            </TableHeaderColumn>
            <TableHeaderColumn
                width="15%"
                dataField="status"
                dataAlign="center"
                dataFormat={statusFormatter}
                dataSort
            >
                Status
            </TableHeaderColumn>
        </BootstrapTable>
    )
}


function EventLogControls(props) {
    return [
        <Col key="Refresh" sm={6}>
            <Button bsStyle="success" onClick={e => props.onRefreshClick(e)}>
                Refresh events log <Glyphicon glyph="retweet" />
            </Button>
        </Col>,
        <Col key="numRecent" sm={6} style={{textAlign: "right"}}>
            <Form onSubmit={e => props.onRefreshClick(e)} inline>
                <ControlLabel>Show events from </ControlLabel>
                <FormControl
                    style={{width: "50px", textAlign: "center", marginLeft: "5px", marginRight: "5px"}}
                    type="text"
                    value={props.value}
                    onChange={e => props.onChangeNumberOfEvents(e)}
                />
                <ControlLabel> last days</ControlLabel>
            </Form>
        </Col>
    ]
}


class EventsLog extends Component {

    constructor(props) {
        super(props)
        this.state = {
            loading: true
        }
    }

    loadRecentEvents(number, notify=false) {
        Client.getRecentEvents(number).then(events => {
            this.props.setRecentEvents(events);
            notify && this.props.addNotification('Events log refreshed', 'info');
        }).then(
            () => this.setState({loading: false})
        ).catch(err => console.log(err))
    }

    componentDidMount() {
        this.loadRecentEvents(this.props.numberOfRecentEventsDays)
    }

    onChangeNumberOfEvents(event) {
        const number = event.target.value;
        if (number > this.props.recentEvents.length) {
            this.loadRecentEvents(number);
        }
        this.props.setNumberOfRecentEventsDays(number);
    }

    handleRefreshClick(event) {
        event.preventDefault();
        this.loadRecentEvents(this.props.numberOfRecentEventsDays, true);
    }

    render() {
        return [
            <PageHeader key="header" id="header">Events log</PageHeader>,
            <Grid key="grid" style={{textAlign: "left"}}>
                {this.state.loading ? <Loading /> :
                [
                    <Row key="controls">
                        <EventLogControls
                            value={this.props.numberOfRecentEventsDays}
                            onRefreshClick={e => this.handleRefreshClick(e)}
                            onChangeNumberOfEvents={e => this.onChangeNumberOfEvents(e)}
                        />
                    </Row>,
                    <Row key="table" style={{marginTop: "20px"}}>
                        <EventsTable events={this.props.recentEvents} />
                    </Row>
                ]
                }
            </Grid>
        ];
    }
}


const mapStateToProps = state => {
    return {
        recentEvents: state.recentEvents,
        numberOfRecentEventsDays: state.numberOfRecentEventsDays
    }
}

const mapDispatchToProps = dispatch => {
    return {
        addNotification: (message, level) => {
            dispatch(addNotification(message, level));
        },
        setNumberOfRecentEventsDays: (number) => {
            dispatch(setNumberOfRecentEventsDays(number));
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
