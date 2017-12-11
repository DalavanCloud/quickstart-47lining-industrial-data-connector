import React, { Component } from 'react';
import { Label, PageHeader, Grid, Row, Col, Button, ButtonGroup, Glyphicon } from 'react-bootstrap';
import Client from '../ApiClient.js'
import { connect } from 'react-redux'
import { piPointList } from './PiPointsActions.js'
import { addNotification, showModal } from '../app/actions.js'
import ConnectedSubscriptionButtons from './SubscribeButton.js'
import ConnectedBatchActionsButtons from './BatchActionsButtons.js'
import {default as SyncPiPointsButton} from './SyncPiPointsButton.js'
import Publish from '../forms/Publish.js'
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table'
import 'react-bootstrap-table/dist/react-bootstrap-table.min.css'
import Loading from '../app/Loading.js'
import { formatTimestamp } from '../utils.js'


class PiPointsList extends Component {
    constructor(props) {
        super(props);
        this.state = {
            checkedPoints: new Set(),
            loading: true
        }
        this.handleCheckboxCheck = this.handleCheckboxCheck.bind(this);
        this.handleCheckAll = this.handleCheckAll.bind(this);
    }

    componentDidMount() {
        Client.getPiPointsList().then(response => {
            this.props.loadPiPoints(response);
        }).then(
            () => this.setState({loading: false})
        ).catch(err => console.log(err));
    }

    handleCheckboxCheck(row, isSelected) {
        let point = row.pi_point;
        if (isSelected) {
            this.setState((prevState, props) => ({
                checkedPoints: prevState.checkedPoints.add(point)
            }));
        } else {
            this.setState(function(prevState, props) {
                prevState.checkedPoints.delete(point)
                return {
                    checkedPoints: prevState.checkedPoints
                }
            });
        }
    }

    handleCheckAll(isSelected, rows) {
        if (isSelected) {
            this.setState({
                checkedPoints: new Set(rows.map(p => p.pi_point))
            })
        } else {
            this.setState({
                checkedPoints: new Set()
            })
        }
    }

    actionsButtonFormatter(cell, row) {
        return (
            <ConnectedSubscriptionButtons pointName={row.pi_point} />
        )
    }

    statusFormatter(cell, row) {
        let status = row.subscription_status;
        let labelStyle = "default";
        switch (status) {
            case 'subscribed':
                labelStyle = "success";
                break;
            case 'unsubscribed':
                labelStyle = "danger";
                break;
            case 'pending':
                labelStyle = "warning";
                break;
            default:
                break;
        }
        return (
            <h4><Label bsStyle={labelStyle}>{status}</Label></h4>
        )
    }

    getUniqueStatuses() {
        const uniqueStatuses = new Set(this.props.piPointsList.map(p => p.subscription_status));
        const result = [...uniqueStatuses].reduce(function(acc, cur, i) {
            acc[cur] = cur;
            return acc;
        }, {});
        return result;
    }

    renderPiPointsTable() {
        const selectRowProp = {
            mode: 'checkbox',
            onSelect: this.handleCheckboxCheck,
            onSelectAll: this.handleCheckAll,
            selected: [...this.state.checkedPoints]
        }
        return (
            <BootstrapTable data={this.props.piPointsList} selectRow={selectRowProp} striped hover>
                <TableHeaderColumn
                    dataField="pi_point"
                    filter={{ type: 'TextFilter' }}
                    dataSort
                isKey>Name
                </TableHeaderColumn>
                <TableHeaderColumn
                    dataField="update_timestamp"
                    dataSort
                    dataFormat={formatTimestamp}
                >
                    Update timestamp
                </TableHeaderColumn>
                <TableHeaderColumn
                    dataField="subscription_status"
                    dataAlign="center"
                    dataFormat={this.statusFormatter}
                    filter={{ type: 'SelectFilter', options: this.getUniqueStatuses(),  condition: 'eq' }}
                    dataSort
                >Status
                </TableHeaderColumn>
                <TableHeaderColumn
                    dataFormat={this.actionsButtonFormatter}
                    tdStyle={{overflow: 'visible'}}
                    dataAlign="center"
                >Actions
                </TableHeaderColumn>
            </BootstrapTable>
        )
    }

    render() {
        const checkedPoints = [...this.state.checkedPoints];
        const publishProps = {
            formSubmitCustomCallback: () => (this.props.addNotification("Publishing in progress...", "info"))
        }

        return (
            <Grid>
                <Row>
                    <Col md={12}>
                        <PageHeader key="A">PiPoints list</PageHeader>
                    </Col>
                </Row>
                {this.state.loading ? <Loading /> :
                    [
                    <Row key="A" style={{marginBottom: '15px'}}>
                        <Col md={5} mdOffset={7}>
                            <ButtonGroup>
                                <Button bsStyle='info' onClick={() => this.props.showModal("Publish", Publish, publishProps)}>Publish all feeds <Glyphicon glyph="cloud-upload"/></Button>
                                <SyncPiPointsButton />
                                <ConnectedBatchActionsButtons points={checkedPoints} />
                            </ButtonGroup>
                        </Col>
                    </Row>,
                    <Row key="B">
                        <Col md={12}>
                            {this.renderPiPointsTable()}
                        </Col>
                    </Row>
                    ]
                }
            </Grid>
        )
    }
}

const mapStateToProps = state => {
    return {
        piPointsList: state.piPointsList
    }
}

const mapDispatchToProps = dispatch => {
    return {
        addNotification: (message, level) => {
            dispatch(addNotification(message, level));
        },
        loadPiPoints: json => {
            dispatch(piPointList(json));
        },
        showModal: (title, modalComponent, props) => {
            dispatch(showModal(title, modalComponent, props));
        }
    }
}

const ConnectedPiPointsList = connect(
    mapStateToProps,
    mapDispatchToProps
)(PiPointsList)

export default ConnectedPiPointsList;
