import React, { Component } from 'react'
import { console } from 'global'
import { toast } from 'react-toastify'

import apiClient from '../../../apiClient'


export default class SyncButton extends Component {

    handleClick() {
        apiClient.syncFeedsList().then(() => {
            toast.info('Feeds List sync request sent')
        }).catch(err => console.log(err));
    }

    render() {
        return (
            <button
                {...this.props}
                className="btn btn-basic"
                onClick={() => this.handleClick()}
            >
                Request Feeds List sync
            </button>
        )
    }
}
