import React, { Component } from 'react'
import { Popover, OverlayTrigger } from 'react-bootstrap'

import apiClient from '../../apiClient'

import { AthenaIcon } from '../../components/icons'


export default class AthenaLink extends Component {
    constructor(props) {
        super(props);
        this.state = {
            athenaDatabase: "",
            athenaNumericTableName: "",
            athenaTextTableName: "",
            athenaUrl: ""
        }
    }

    componentDidMount() {
        apiClient.getAthenaInfo().then(json => (
            this.setState({
                athenaDatabase: json.database_name,
                athenaNumericTableName: json.numeric_table_name,
                athenaTextTableName: json.text_table_name,
                athenaUrl: json.url
            })
        )).catch(err => console.error(err));
    }

    render() {
        const { athenaDatabase, athenaNumericTableName, athenaTextTableName, athenaUrl } = this.state;
        const helpPopover = (
            <Popover
                id="popover-trigger-click"
                title="Amazon Athena"
                style={{fontWeight: "100"}}
            >
                In order to explore your data select <strong>{athenaDatabase}</strong> database and then <strong>{athenaNumericTableName}</strong> or <strong>{athenaTextTableName}</strong> table.
            </Popover>
        )
        return (
            <OverlayTrigger trigger={['hover', 'focus']} placement="bottom" overlay={helpPopover}>
                <a href={athenaUrl} target="_blank">
                    <AthenaIcon /> Explore data
                </a>
            </OverlayTrigger>
        )
    }
}
