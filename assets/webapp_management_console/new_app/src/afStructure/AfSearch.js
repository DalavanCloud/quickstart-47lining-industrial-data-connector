import React, { Component } from 'react'
import { Form, Col, FormControl, Button, FormGroup, ControlLabel, Glyphicon } from 'react-bootstrap'
import Client from '../ApiClient.js'
import { connect } from 'react-redux'
import { searchResults } from './AfStructureActions.js'
import ConnectedBatchActionsButtons from '../piPoints/BatchActionsButtons.js'
import { addNotification } from '../app/actions.js'
import { GridLoader } from 'halogenium'

import './AfSearch.css'

const initialState = {
    assetsField: "",
    assetsQuery: "",
    attributesField: "",
    attributesQuery: "",
    searchInProgress: false
};

class AfSearch extends Component {
    constructor(props) {
        super(props);
        this.state = initialState
        this.handleInputChange = this.handleInputChange.bind(this);
    }

    handleSearch() {
        this.setState({
            searchInProgress: true
        });
        const searchJson = {
            assetsQuery: this.state.assetsQuery,
            assetsField: this.state.assetsField,
            attributesQuery: this.state.attributesQuery,
            attributesField: this.state.attributesField
        };
        Client.searchAfStructure(searchJson).then(json => {
            this.props.dispatch(searchResults(json));
        }).then(() => {
            this.setState({
                searchInProgress: false
            });
            if (Object.getOwnPropertyNames(this.props.searchResults).length === 0) {
                this.props.dispatch(addNotification("No results found", "warning"));
            }
        });
    }

    handleResetSearch() {
        this.setState(initialState);
        this.props.dispatch(searchResults({}));
    }

    getUniquePoints() {
        var points = []
        for (let assetPath in this.props.searchResults) {
            for (let attribute of this.props.searchResults[assetPath]['attributes']) {
                if (attribute.point !== null) {
                    points.push(attribute.point.name);
                }
            }
        }
        var uniquePoints = new Set(points);
        return [...uniquePoints];
    }

    handleInputChange(event) {
        const target = event.target;
        const name = target.name;
        const value = target.value;
        if (name === 'assetsQuery' || name === 'attributesQuery') {
            this.setState({
                [name]: value
            });
        } else if (name === 'assetsField' || name === 'attributesField') {
            this.setState({
                [name]: value
            });
        }
    }

    render() {
        const uniquePoints = this.getUniquePoints();
        const searchDisabled = Object.getOwnPropertyNames(this.props.afData.menu).length === 0 && this.props.afData.nodes.length === 0;
        const fieldsetClass = this.state.searchInProgress ? 'inactive' : 'active';
        return (
            [
            <GridLoader key="GridLoader" color="#DDD" hidden={!this.state.searchInProgress} className='grid-loader' />,
            <Form key="Form" horizontal>
                <fieldset className={fieldsetClass}>
                    <FormGroup controlId="formHorizontalAssets">
                        <Col componentClass={ControlLabel} sm={2}>Search assets:</Col>
                        <Col sm={2}>
                            <FormControl name="assetsField" onChange={this.handleInputChange} componentClass="select" placeholder="select" value={this.state.assetsField}>
                                <option value="name">Name</option>
                                <option value="description">Description</option>
                                <option value="categories">Categories</option>
                                <option value="template">Template</option>
                                <option value="path">AfPath</option>
                            </FormControl>
                        </Col>
                        <Col sm={5}>
                            <FormControl
                                name="assetsQuery"
                                onChange={this.handleInputChange}
                                type="text"
                                placeholder="Search for..."
                                size="50"
                                value={this.state.assetsQuery}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup controlId="formHorizontalAttributes">
                        <Col componentClass={ControlLabel} sm={2}>Filter attributes:</Col>
                        <Col sm={2}>
                            <FormControl name="attributesField" onChange={this.handleInputChange} componentClass="select" placeholder="select" value={this.state.attributesField}>
                                <option value="name">Name</option>
                                <option value="description">Description</option>
                                <option value="categories">Categories</option>
                            </FormControl>
                        </Col>
                        <Col sm={5}>
                            <FormControl
                                name="attributesQuery"
                                onChange={this.handleInputChange}
                                type="text"
                                placeholder="Search for..."
                                size="50"
                                value={this.state.attributesQuery}
                            />
                        </Col>
                    </FormGroup>
                    <FormGroup>
                        <Col smOffset={2} sm={1}>
                            <Button type="button" onClick={() => this.handleSearch()} disabled={searchDisabled}>
                                Search{' '}<Glyphicon glyph="search" />
                            </Button>
                        </Col>
                        <Col smOffset={1} sm={2}>
                            <Button type="button" bsStyle="danger" onClick={() => this.handleResetSearch()} disabled={searchDisabled}>
                                Reset search{' '}<Glyphicon glyph="remove" />
                            </Button>
                        </Col>
                        <Col sm={2}>
                            <ConnectedBatchActionsButtons points={uniquePoints}/>
                        </Col>
                    </FormGroup>
                </fieldset>
            </Form>
            ]
        )
    }
}

const mapStateToProps = state => {
    return {
        searchResults: state.searchResults,
        piPointsList: state.piPointsList,
        afData: state.afData
    }
}

const ConnectedAfSearch = connect(
    mapStateToProps
)(AfSearch)

export default ConnectedAfSearch;
