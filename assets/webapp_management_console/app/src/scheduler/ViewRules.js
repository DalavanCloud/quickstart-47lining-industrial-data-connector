import React, { Component } from 'react'

import Client from '../ApiClient.js'

import { StructureIcon, FeedsIcon } from '../common/icons.js'
import Spinner from '../app/Loading.js'

import Scheduler from './Scheduler.js'


export default class ViewRules extends Component {

    constructor(props) {
        super(props)
        this.state = {
            structureCron: '',
            feedsCron: ''
        }
    }

    componentDidMount() {
        Client.getSchedulerRules().then(
            rules => this.setState({
                structureCron: rules.structure.cron,
                feedsCron: rules.feeds.cron
            })
        )
    }

    render() {
        return (
            <div className="scheduler">
                <div className="container-fluid">
                    <div className="content">
                        <div className="form-box">
                            <div className="text-center branding">
                                <StructureIcon color="rgba(0,0,0,0.1)" />
                            </div>
                            <div className="text">
                                <h2>Schedule Structure sync</h2>
                            </div>
                            {this.state.structureCron
                                ? <Scheduler
                                    cron={this.state.structureCron}
                                    type="structure"
                                />
                                : <Spinner text="" timeout={1000} />}
                        </div>
                        <div className="form-box">
                            <div className="text-center branding">
                                <FeedsIcon color="rgba(0,0,0,0.1)" />
                            </div>
                            <div className="text">
                                <h2>Schedule Feeds List sync</h2>
                            </div>
                            {this.state.feedsCron
                                ? <Scheduler
                                    cron={this.state.feedsCron}
                                    type="feeds"
                                />
                                : <Spinner text="" timeout={1000} />}
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}
