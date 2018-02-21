import React, { Component } from 'react';
import { Table, Checkbox, Grid, Row, Col, Button } from 'react-bootstrap';
import { connect } from 'react-redux'
import Client from '../ApiClient.js'
import { addNotification } from '../app/actions.js'


class AfSearchResults extends Component {
    constructor(props) {
        super(props);
        this.state = {};
        this.handleCheck = this.handleCheck.bind(this);
        this.handleCheckAll = this.handleChangeAll.bind(this);
        this.handleSubscribeButton = this.handleSubscribeButton.bind(this);
    }

    handleCheck(path) {
        var newState = {};
        if (path in this.state) {
            newState[path] = !this.state[path]
            this.setState(newState);
        } else {
            newState[path] = true;
            this.setState(newState);
        }
    }

    handleChangeAll(newValue) {
        var newState = {};
        this.props.searchResults.forEach(item => {
            newState[item.path] = newValue;
        });
        this.setState(newState);
    }

    handleSubscribeButton() {
        var points = this.props.searchResults.filter(r => {
            return r.point !== null && r.path in this.state && this.state[r.path] === true;
        }).map(r => {
            return r.point.name;
        });
        var uniquePoints = new Set(points);
        Client.subscribeToPiPoints([...uniquePoints]).then(response => {
            this.props.addNotification('Subscribed to points: ' + [...uniquePoints].join(", "), 'info');
        })
    }

    render () {
        const searchResults = this.props.searchResults;
        var results = searchResults.map(item => {
            var isChecked = false;
            if (item.path in this.state && this.state[item.path] === true) {
                isChecked = true;
            }
            return <ResultRow result={item} key={item.path} checked={isChecked} handleCheck={this.handleCheck} />
        });
        return (
            <Grid>
                <Row>
                    <Col md={3}>
                        <h3 key="A">Search results:</h3>
                    </Col>
                    <Col className="pull-right">
                        <Button bsStyle="success" onClick={() => this.handleSubscribeButton()}>Subscribe to selected PiPoints</Button>
                    </Col>
                </Row>
                <Row>
                    <Table key="B" striped bordered hover>
                        <thead>
                            <tr>
                                <th><Button bsSize="xsmall" onClick={() => this.handleChangeAll(true)} >All</Button><br />
                                <Button bsSize="xsmall" onClick={() => this.handleChangeAll(false)} >None</Button></th>
                                <th>Name</th>
                                <th>Description</th>
                                <th>Value</th>
                                <th>Asset name</th>
                                <th>Has PiPoint</th>
                                <th>Path</th>
                                <th>Categories</th>
                            </tr>
                        </thead>
                        <tbody>
                            {results}
                        </tbody>
                    </Table>
                </Row>
            </Grid>
        )
    }
}

class ResultRow extends Component {

    render () {
        const name = this.props.result.name;
        const description = this.props.result.description;
        const value = this.props.result.value;
        const path = this.props.result.path;
        const asset = this.props.result.asset;
        const checked = this.props.checked;
        const hasPiPoint = this.props.result.point !== null;
        const categories = this.props.result.categories.map((category) => {
            return <li key={category.name}>{category.name} {category.description !== "" && (<span>- {category.description}</span>)}</li>
        });
        return (
            <tr>
                <td>
                    {checked ? (<Checkbox checked onChange={() => this.props.handleCheck(path)}></Checkbox>) : (<Checkbox onChange={() => this.props.handleCheck(path)}></Checkbox>)}
                </td>
                <td>{name}</td>
                <td>{description}</td>
                <td>{value === "" && value.value}</td>
                <td>{asset}</td>
                <td>{hasPiPoint ? ("YES"):("NO")}</td>
                <td>{path}</td>
                <td>
                    <ul>
                    {categories}
                    </ul>
                </td>
            </tr>
        )
    }
}

const mapStateToProps = state => {
    return {
        searchResults: state.searchResults
    }
}

const mapDispatchToProps = dispatch => {
    return {
        addNotification: (message, level) => {
            dispatch(addNotification(message, level));
        }
    }
}

const ConnectedAfSearchResults = connect(
    mapStateToProps,
    mapDispatchToProps
)(AfSearchResults)

export default ConnectedAfSearchResults;
