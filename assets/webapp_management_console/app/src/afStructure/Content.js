import React, { Component } from 'react'
import { Table, Button, ButtonGroup, Row, Col, Checkbox } from 'react-bootstrap'
import { connect } from 'react-redux'
import Client from '../ApiClient.js'
import { addNotification } from '../app/actions.js'
import ConnectedSubscriptionButtons from '../piPoints/SubscribeButton.js'
import { changeAttributes } from './AfStructureActions.js'

import { formatTimestamp } from '../utils.js'

import './Content.css'


function AssetName({text}) {
    return (
        <h3 id="asset-name" className="page-header">{text}</h3>
    );
}

function AssetData(props) {
    let categories = []
    if (props.categories) {
        categories = props.categories.map(c => <li key={c}>{c}</li>);
    }
    return (
        <Row>
            <Col sm={3}>
                <strong>Description:</strong>
                <p>{props.description}</p>
            </Col>
            <Col sm={3}>
                <strong>Template:</strong>
                <p>{props.template}</p>
            </Col>
            <Col sm={3}>
                <strong>Categories:</strong>
                <ul>
                    {categories}
                </ul>
            </Col>
        </Row>
    );
}

class AttributesTableItem extends Component {
    constructor(...args) {
        super(...args);
        this.state = {
            open: false
        };
    }

    renderPoint(point) {
        if (point !== null) {
            return (
            [
                <strong key="A">Point</strong>,
                <p key="B"><strong>{point.id}</strong> {point.name}</p>
            ]
            );
        } else {
            return '';
        }
    }

    renderSubscribeButton(attribute) {
        if (attribute.point !== null) {
            return (
                <ConnectedSubscriptionButtons pointName={attribute.point.name} />
            );
        } else {
            return '';
        }
    }

    handleAttributeSelect(attribute) {
        const searchedAttributes = this.props.asset in this.props.searchResults ? this.props.searchResults[this.props.asset]['attributes'] : [];
        var newSearchAttributes = searchedAttributes.filter((item) => {
            return item.name !== attribute.name;
        });
        if (searchedAttributes.length === newSearchAttributes.length) {
            newSearchAttributes.push(attribute);
        }
        this.props.changeAttributes(this.props.asset, newSearchAttributes);
    }

    handleSubscribeButtonClick(pointName) {
        Client.subscribeToPiPoint(pointName).then(response => {
            this.props.addNotification('Subscribed to point ' + pointName, 'info')
        })
    }

    renderLabel(status) {
        var labelStyle = "default";
        switch (status) {
            case 'subscribed':
                labelStyle = "success";
                break;
            case 'unsubscribed':
                labelStyle = "danger";
                break;
            case 'pending':
                labelStyle = "warning";
                break;
            default:
                break;
        }
        return (
            <Button bsSize="small" bsStyle={labelStyle}><strong>{status}</strong></Button>
        )
    }

    render() {
        const searchedAttributes = this.props.asset in this.props.searchResults ? this.props.searchResults[this.props.asset]['attributes'] : [];
        const { attribute } = this.props
        const descriptionItemClass = this.state.open ? "open" : "closed"
        var checked = false;
        for (var searchAttribute of searchedAttributes) {
            if (attribute.name === searchAttribute.name) {
                checked = true;
            }
        }
        const cssClass = checked ? "attributeTableMainItem marked" : "attributeTableMainItem";

        return (
            [
                <tr key="A" className={cssClass}>
                    <td><Checkbox checked={checked} onChange={() => this.handleAttributeSelect(attribute)}/></td>
                    <td>{attribute.name}</td>
                    <td>{attribute.value.value}</td>
                    <td>{formatTimestamp(attribute.value.timestamp)}</td>
                    <td>{attribute.type}</td>
                    <td>
                        {
                            attribute.point !== null ?
                                this.renderLabel(ConnectedSubscriptionButtons.getSubscriptionStatus(attribute.point.name, this.props.piPointsList)) : ''
                        }
                    </td>
                    <td>{this.renderSubscribeButton(attribute)}</td>
                    <td>
                        <Button onClick={() => this.setState({ open: !this.state.open })}>Details</Button>
                    </td>
                </tr>,
                <tr key="B" className={`attributeTableDescriptionItem ${descriptionItemClass}`}>
                    <td colSpan="2">
                        <strong>Description</strong><p>{attribute.description}</p>
                    </td>
                    <td colSpan="2">
                        <strong>Categories</strong>
                        <ol>
                            {
                                attribute.categories.map((category, index) => (
                                    <li key={category}>{category['name']}</li>
                                ))
                            }
                        </ol>
                    </td>
                    <td colSpan="3">
                        {this.renderPoint(attribute.point)}
                    </td>

                </tr>
            ]
        );
    }
}

function AttributesTable(props) {
    const { data } = props;
    return (
        <Table responsive>
            <thead>
                <tr>
                    <th></th>
                    <th>Name</th>
                    <th>Value</th>
                    <th>Value timestamp</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Actions</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {
                    Object.keys(data).map((key, index) => (
                        <ConnectedAttributeTableItem id={index} key={key} attribute={data[key]} />
                    ))
                }
            </tbody>
        </Table>
    );
}

function Attributes(props) {
    if (props.data === null || props.data.length === 0) {
        return '';
    } else {
        return (
            <div>
                <Row>
                    <Col md={4}>
                        <h4>Attributes:</h4>
                    </Col>
                    <Col mdOffset={9}>
                        <ConnectedSelectAttributesButton attributes={props.data} />
                    </Col>
                </Row>
                <Row>
                    <Col>
                    <AttributesTable data={props.data} />
                    </Col>
                </Row>
            </div>
        );
    }
}

class SelectAttributesButton extends Component {
    handleSelectAll() {
        this.props.changeAttributes(this.props.asset, this.props.attributes);
    }

    handleDeselectAll() {
        this.props.changeAttributes(this.props.asset, []);
    }

    render() {
        return (
            <ButtonGroup>
                <Button onClick={() => this.handleSelectAll()}>Select all</Button>
                <Button onClick={() => this.handleDeselectAll()}>Deselect all</Button>
            </ButtonGroup>
        )
    }
}

class Content extends Component {
    getAssetProperties(asset) {
        var node = this.props.nodes[asset];

        if (node === undefined) {
            node = {
                description: 'Select Asset from menu on left',
                name: 'Management console',
                attributes: []
            };
        }
        return {
            asset: node.name,
            description: node.description,
            attributes: node.attributes,
            template: node.template,
            categories: node.categories
        };
    }

    render() {
        var assetProperties = this.getAssetProperties(this.props.asset);
        return (
            [
                <AssetName key={`${assetProperties.asset}_name`} text={assetProperties.asset} />,
                <AssetData key={`${assetProperties.asset}_description`} description={assetProperties.description} template={assetProperties.template} categories={assetProperties.categories} />,
                <Attributes key={`${assetProperties.asset}_attributes`} data={assetProperties.attributes} />
            ]
        );
    }
}


const mapStateToProps = state => {
    return {
        asset: state.selectedAsset,
        nodes: state.afData.nodes,
        searchResults: state.searchResults,
        piPointsList: state.piPointsList
    }
}

const mapDispatchToProps = dispatch => {
    return {
        addNotification: (message, level) => {
            dispatch(addNotification(message, level));
        },
        changeAttributes: (assetName, newAttributes) => {
            dispatch(changeAttributes(assetName, newAttributes));
        }
    }
}

const ConnectedAttributeTableItem = connect(
    mapStateToProps,
    mapDispatchToProps
)(AttributesTableItem)

const ConnectedContent = connect(
    mapStateToProps,
    mapDispatchToProps
)(Content)

const ConnectedSelectAttributesButton = connect(
    mapStateToProps,
    mapDispatchToProps
)(SelectAttributesButton);

export default ConnectedContent;
