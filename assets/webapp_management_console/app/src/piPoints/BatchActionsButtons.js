import React, { Component } from 'react';
import { DropdownButton, MenuItem } from 'react-bootstrap'
import Interpolate from '../forms/Interpolate.js'
import Backfill from '../forms/Backfill.js'
import Client from '../ApiClient.js'
import { addNotification, showModal } from '../app/actions.js'
import { connect } from 'react-redux'
import SubscriptionButtons from './SubscribeButton.js'


class BatchActionsButtons extends Component {

    getPointsStatus() {
        let checkedPointsStatus = {}
        for (const point of this.props.points) {
            checkedPointsStatus[point] = SubscriptionButtons.getSubscriptionStatus(point, this.props.piPointsList);
        }
        return checkedPointsStatus;
    }

    handleBatchSubscribe(allPoints = false) {
        if (allPoints) {
            Client.subscribeToAllPiPoints().then(response => {
                this.props.dispatch(addNotification('Subscribed to all PiPoints', 'info'));
            });
        } else {
            const pointsStatus = this.getPointsStatus();
            const pointsToSubscribe = this.props.points.filter(
                point => pointsStatus[point] !== 'subscribed'
            )
            if (pointsToSubscribe.length > 0) {
                Client.subscribeToPiPoints(pointsToSubscribe).then(response => {
                    this.props.dispatch(addNotification('Subscribed to PiPoints: ' + pointsToSubscribe.join(", "), 'info'));
                });
            } else {
                this.props.dispatch(addNotification('All requested points are already subscribed', 'warning'));
            }
        }
    }

    handleBatchUnsubscribe(allPoints = false) {
        if (allPoints) {
            Client.unsubscribeFromAllPiPoints().then(response => {
                this.props.dispatch(addNotification('Unsubscribed from all PiPoints', 'info'));
            });
        } else {
            const pointsStatus = this.getPointsStatus();
            const pointsToUnubscribe = this.props.points.filter(
                point => pointsStatus[point] !== 'unsubscribed'
            )
            if (pointsToUnubscribe.length > 0) {
                Client.unsubscribeFromPiPoints(pointsToUnubscribe).then(response => {
                    this.props.dispatch(addNotification('Unsubscribed from PiPoints: ' + pointsToUnubscribe.join(", "), 'info'));
                });
            } else {
                this.props.dispatch(addNotification('All requested points are already unsubscribed', 'warning'));
            }
        }
    }

    render() {
        const noPointsSelected = this.props.points.length === 0;
        return (
            <DropdownButton bsStyle="primary" title="Batch actions" id="actions-dropdown">
                <MenuItem onClick={() => this.handleBatchSubscribe(noPointsSelected)}>
                    Subscribe {noPointsSelected ? 'all' : ''}
                </MenuItem>
                <MenuItem onClick={() => this.handleBatchUnsubscribe(noPointsSelected)}>
                    Unsubscribe {noPointsSelected ? 'all' : ''}
                </MenuItem>
                <MenuItem
                    onClick={() => this.props.dispatch(
                        showModal(
                            "Interpolate",
                            Interpolate,
                            {points: this.props.points, allPoints: noPointsSelected}
                        )
                    )}
                >
                    Interpolate
                </MenuItem>
                <MenuItem
                    onClick={() => this.props.dispatch(
                        showModal(
                            "Backfill",
                            Backfill,
                            {points: this.props.points, allPoints: noPointsSelected}))}
                >
                    Backfill
                </MenuItem>
            </DropdownButton>
        )
    }
}

const mapStateToProps = state => {
    return {
        piPointsList: state.piPointsList
    }
}

const ConnectedBatchActionsButtons = connect(mapStateToProps)(BatchActionsButtons);
export default ConnectedBatchActionsButtons;
