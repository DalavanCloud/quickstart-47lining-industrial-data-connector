import React, { Component } from 'react';
import { Label, PageHeader, Grid, Row, Col, Button, ButtonGroup, Glyphicon, Checkbox } from 'react-bootstrap';
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
import './PiPointsList.css'


class PiPointsList extends Component {
    constructor(props) {
        super(props);
        this.state = {
            checkedPoints: new Set(),
            loading: true
        }
    }

    componentDidMount() {
        this.loadPiPoints();
    }

    loadPiPoints() {
        this.setState({
            loading: true
        });
        Client.getPiPointsList().then(response => {
            this.props.loadPiPoints(response);
        }).then(
            () => this.setState({loading: false})
        ).catch(err => console.log(err));
    }

    handleCheckboxCheck(event, point, checked) {
        if (!checked) {
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

    handleCheckAll(event) {
        let visiblePoints = new Set(this.bootstrapTable.state.data.map(p => p.pi_point));
        if (!this.state.selectAll) {
            this.setState((prevState, props) => ({
                checkedPoints: new Set([...visiblePoints, ...prevState.checkedPoints]),
                selectAll: true
            }));
        } else {
            this.setState((prevState, props) => {
                let difference = new Set([...prevState.checkedPoints].filter(x => !visiblePoints.has(x)));
                return {
                    checkedPoints: difference,
                    selectAll: false
                }
            });
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

    checkboxFormatter(cell, row) {
        const checked = this.state.checkedPoints.has(row.pi_point);
        return (
            <Checkbox
                checked={checked}
                onChange={(event) => this.handleCheckboxCheck(event, row.pi_point, checked)}
            />
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

    onPageChange(page, sizePerPage) {
        this.setState({selectAll: false, activePage: page, sizePerPage: sizePerPage});
    }

    renderPiPointsTable() {
        const options = {
            page: this.state.activePage,
            sizePerPage: this.state.sizePerPage,
            onPageChange: (...args) => this.onPageChange(...args)
        }

        return (
            <BootstrapTable
                data={this.props.piPointsList}
                striped
                hover
                pagination
                options={options}
                ref={bootstrapTable => this.bootstrapTable = bootstrapTable}
            >
                <TableHeaderColumn
                    width="5%"
                    dataAlign="center"
                    dataFormat={(...args) => this.checkboxFormatter(...args)}
                >
                    <Checkbox
                        checked={this.state.selectAll}
                        onChange={e => this.handleCheckAll(e)}
                    />
                </TableHeaderColumn>
                <TableHeaderColumn
                    dataField="pi_point"
                    filter={{ type: 'TextFilter' }}
                    dataSort
                    isKey
                >
                    Name
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
                >
                    Status
                </TableHeaderColumn>
                <TableHeaderColumn
                    dataFormat={this.actionsButtonFormatter}
                    tdStyle={{overflow: 'visible'}}
                    dataAlign="center"
                >
                    Actions
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
                        <Col md={1}>
                            <Button bsStyle='success' onClick={() => this.loadPiPoints()}>Refresh <Glyphicon glyph="refresh" /></Button>
                        </Col>
                        <Col md={5} mdOffset={6}>
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
