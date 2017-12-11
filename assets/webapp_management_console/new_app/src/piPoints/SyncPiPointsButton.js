import React, { Component } from 'react';
import { Button, Glyphicon } from 'react-bootstrap';
import Client from '../ApiClient.js'
import { connect } from 'react-redux'
import { addNotification } from '../app/actions.js'


class SyncPiPointsButton extends Component {

    handlePiPointsSync() {
        Client.syncPiPointsList().then(response => {
            this.props.dispatch(addNotification('PiPoints sync request sent', 'info'));
        }).catch(err => console.log(err));
    }

    render() {
        return (
            <Button bsStyle="success" onClick={() => this.handlePiPointsSync()}>
                Request Pi Points sync <Glyphicon glyph="retweet" />
            </Button>
        )
    }
}

const ConnectedSyncPiPointsButton = connect()(SyncPiPointsButton);
export default ConnectedSyncPiPointsButton;