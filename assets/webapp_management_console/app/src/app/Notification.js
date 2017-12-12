import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Alert, Panel, Table } from 'react-bootstrap'
import { removeNotification } from './actions.js'

import './Notification.css'

class Notification extends Component {

    renderExceptionTable(message) {
        return (
            <Table className="errorTable" bordered responsive>
                <tbody>
                    <tr>
                        <td>Exception</td>
                        <td>{message.exception}</td>
                    </tr>
                    <tr>
                        <td>Description</td>
                        <td>{message.description}</td>
                    </tr>
                </tbody>
            </Table>
        )
    }

    renderNotification(detailed, message) {
        if (detailed) {
            console.warn(message.traceback);
            return (
                <div style={{textAlign: "left"}}>
                    <h4>{message.message}</h4>
                    <p>Please try again</p>
                    <Panel className="errorPanel" collapsible header="Details" eventKey="1"  bsStyle="warning">
                        {this.renderExceptionTable(message)}
                    </Panel>
                </div>
            );
        } else {
            return <p>{message}</p>;
        }
    }

    render() {
        if (this.props.notifications.length > 0) {
            let notifications = this.props.notifications;
            return (notifications.map((item, index) => {
                return (
                    <Alert
                        key={index}
                        bsStyle={item.level}
                        onDismiss={() => this.props.removeNotification(index)}
                    >
                        {this.renderNotification(item.detailed, item.message)}
                    </Alert>
                );
            })
            )
        } else {
            return '';
        }
    }
}

function mapStateToProps(state) {
    return {
        notifications: state.notifications
    };
}

function mapDispatchToProps(dispatch) {
    return {
        removeNotification: (index) => {
            dispatch(removeNotification(index));
        }
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(Notification);
