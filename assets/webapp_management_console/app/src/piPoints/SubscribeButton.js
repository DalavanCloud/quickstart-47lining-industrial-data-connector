import React, { Component } from 'react'
import { Button, Glyphicon, DropdownButton, MenuItem, Tooltip, OverlayTrigger } from 'react-bootstrap'
import Client from '../ApiClient.js'
import { connect } from 'react-redux'
import { addNotification } from '../app/actions.js'


class SubscriptionButtons extends Component {
    static getSubscriptionStatus(pointName, piPointsList) {
        const statusArray = piPointsList.filter(point => {
            return point.pi_point === pointName;
        }).map(point => {
            return point.subscription_status
        });
        return statusArray.length !== 0 ? statusArray[0] : "unknown";
    }

    render () {
        const tooltipAlreadySubscribed = (
            <Tooltip id="tooltipAlreadySubscribed"><strong>ManagedFeed for this PI Point already exists</strong></Tooltip>
        )
        const tooltipAlreadyUnsubscribed = (
            <Tooltip id="tooltipAlreadyUnsubscribed"><strong>ManagedFeed for this PI Point doesn't exist</strong></Tooltip>
        )
        const tooltipStatusPending = (
            <Tooltip id="tooltipStatusPending"><strong>ManagedFeed for this PI Point is pending</strong></Tooltip>
        )
        const tooltipStatusUnknown = (
            <Tooltip id="tooltipStatusUnknown"><strong>ManagedFeed for this PI Point is in unknown state</strong></Tooltip>
        )
        const statusTooltipMap = {
            'subscribed': tooltipAlreadySubscribed,
            'unsubscribed': tooltipAlreadyUnsubscribed,
            'pending': tooltipStatusPending,
            'unknown': tooltipStatusUnknown
        }

        const status = SubscriptionButtons.getSubscriptionStatus(this.props.pointName, this.props.piPointsList);
        const pointName = this.props.pointName;
        return (

            <DropdownButton bsStyle="info" title="Actions" id={`dropdown-actions-${pointName}`}>
                <MenuItem eventKey="1">
                    <SubscribeButton
                        pointName={pointName}
                        status={status}
                        tooltip={statusTooltipMap[status]}
                        dispatch={this.props.dispatch}
                    />
                </MenuItem>
                <MenuItem eventKey="2">
                    <UnsubscribeButton
                        pointName={pointName}
                        status={status}
                        tooltip={statusTooltipMap[status]}
                        dispatch={this.props.dispatch}
                    />
                </MenuItem>
            </DropdownButton>

        )
    }
}

class SubscribeButton extends Component {

    handleSubscribeButtonClick(pointName) {
        Client.subscribeToPiPoint(pointName).then(response => {
            this.props.dispatch(addNotification('Subscribed to point ' + pointName, 'info'));
        })
    }

    render() {
        const pointName = this.props.pointName;
        const status = this.props.status;
        const isDisabled = status !== 'unsubscribed';
        if (isDisabled) {
            return (
                <OverlayTrigger placement="top" overlay={this.props.tooltip}>
                    <div style={{cursor: 'not-allowed'}}>
                        <Button
                            style={{pointerEvents: 'none'}}
                            bsStyle="primary"
                            onClick={() => this.handleSubscribeButtonClick(pointName)}
                            disabled
                        >
                            Subscribe
                            <Glyphicon glyph="flash" />
                        </Button>
                    </div>
                </OverlayTrigger>
            )
        } else {
            return (
                <Button
                bsStyle="primary"
                onClick={() => this.handleSubscribeButtonClick(pointName)}>
                Subscribe
                <Glyphicon glyph="flash" />
            </Button>
            )
        }
    }
}

class UnsubscribeButton extends Component {

    handleUnsubscribeButtonClick(pointName) {
        Client.unsubscribeFromPiPoint(pointName).then(response => {
            this.props.dispatch(addNotification('Unsubscribed from point ' + pointName, 'info'));
        })
    }

    render() {
        const pointName = this.props.pointName;
        const status = this.props.status;
        const isDisabled = status !== 'subscribed';
        if (isDisabled) {
            return (
                <OverlayTrigger placement="top" overlay={this.props.tooltip}>
                    <div style={{cursor: 'not-allowed'}}>
                        <Button
                            style={{pointerEvents: 'none'}}
                            bsStyle="danger"
                            onClick={() => this.handleUnsubscribeButtonClick(pointName)}
                            disabled
                        >
                            Unsubscribe <Glyphicon glyph="remove" />
                        </Button>
                    </div>
                </OverlayTrigger>
            )
        } else {
            return (
                <Button
                    bsStyle="danger"
                    onClick={() => this.handleUnsubscribeButtonClick(pointName)}>
                    Unsubscribe <Glyphicon glyph="remove" />
                </Button>
            )
        }

    }
}

const mapStateToProps = state => {
    return {
        piPointsList: state.piPointsList
    }
}

const ConnectedSubscriptionButtons = connect(
    mapStateToProps
)(SubscriptionButtons)

export default ConnectedSubscriptionButtons;
