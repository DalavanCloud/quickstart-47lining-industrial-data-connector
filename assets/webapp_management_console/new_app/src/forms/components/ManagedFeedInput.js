import React, { Component } from 'react'
import {
    Col, FormGroup, ControlLabel
} from 'react-bootstrap'
import Client from '../../ApiClient.js'

import Select from 'react-select'
import 'react-select/dist/react-select.css'

import '../Forms.css'


class ManagedFeedInput extends Component {

    constructor(...args) {
        super(...args);
        this.state = {feeds: [], selected: []};
        if (this.props.feeds) {
            this.state = {selected: this.getSelectOptions(this.props.feeds), feeds: this.props.feeds}
        }
    }

    static validator(feeds) {
        if (feeds.length > 0)
            return 'success';
        return null;
    }

    componentDidMount() {
        Client.getSubscribedFeeds().then(
            json => {
                this.setState({feeds: Array.from(new Set([...this.state.feeds, ...json]))});
            }
        ).catch(err => console.log(err))
    }

    getSelectOptions(feeds = this.state.feeds) {
        return feeds.reduce((arr, key) => ([...arr, {value: key, label: key}]), []);
    }

    handleOnChange(value) {
        let feeds = undefined;
        if (this.props.multi) {
            feeds = value.reduce((arr, item) => ([...arr, item.value]), []);
            this.setState({ selected: value });
        } else {
            feeds = [value.value];
            this.setState({ selected: [value] });
        }
        this.props.onChange('feeds', feeds);
    }

    render() {
        const validationState = this.constructor.validator(this.state.selected);

        const value = this.props.multi ? this.state.selected : this.state.selected[0]
        return (
            <FormGroup
                controlId="managedFeedInput"
                validationState={validationState}
            >
                <Col componentClass={ControlLabel} sm={2}>
                    PI Points
                </Col>
                <Col sm={10}>
                    <Select
                        className="onTop"
                        name="select-feed"
                        closeOnSelect={false}
                        multi={this.props.multi}
                        value={value}
                        clearable={false}
                        options={this.getSelectOptions()}
                        onChange={feed => this.handleOnChange(feed)}
                        disabled={this.props.disabled}
                    />
                </Col>
            </FormGroup>
        )
    }
}

export default ManagedFeedInput
