import React, { Component } from 'react'
import pluralize from 'pluralize'
import { Button } from 'react-bootstrap'

import Client from '../ApiClient.js'
import { getPayloadFromProps } from './utils.js'


class Unsubscribe extends Component {

    handleClick = () => {
        Client.unsubscribeFromFeeds(getPayloadFromProps(this.props));
        this.props.onSubmitCallback();
    }

    render() {
        const { feeds } = this.props;
        const totalCount = feeds ? feeds.length : this.props.feedsTotalCount;
        return (
            <div>
                <p>You are going to unsubscribe from {totalCount} {pluralize('feed', totalCount)}</p>
                {totalCount > 100 && <p>This operation can take a long time!</p>}
                <Button className="btn-primary" onClick={this.handleClick}>
                    {totalCount > 100 ? 'I understand, continue' : 'Continue'}
                </Button>
            </div>
        )
    }
}

export default Unsubscribe;
