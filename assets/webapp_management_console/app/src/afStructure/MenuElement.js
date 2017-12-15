import React, { Component } from 'react'
import { connect } from 'react-redux'
import { ListGroupItem, Collapse, Glyphicon } from 'react-bootstrap'
import { selectAsset } from './AfStructureActions.js'

import './MenuElement.css'

function isEmpty(obj) {
    return (obj === 'undefined' || Object.getOwnPropertyNames(obj).length === 0);
}

class MenuElement extends Component {
    constructor(...args) {
        super(...args);

        this.state = {};
    }

    isMarked(path, serachResults) {
        var result = false;
        for (var key in serachResults) {
            if (key.indexOf(path) === 0) {
                result = true;
            }
        }
        return result;
    }

    renderSingleElement(glyph, glyphStyle) {
        var cssClass = this.props.aset === this.props.path ? "current" : "notCurrent";
        if (this.isMarked(this.props.path, this.props.searchResults)) {
            cssClass += " marked";
        }
        return (
            <ListGroupItem className={cssClass}>
                <div onClick={event => {event.stopPropagation(); this.props.selectAsset(this.props.path);}}>
                    <Glyphicon onClick={event => {event.stopPropagation(); this.setState({ open: !this.state.open })}} style={glyphStyle} glyph={glyph} />
                    {this.props.name}
                </div>
            </ListGroupItem>
        );
    }

    render() {
        const indent = 20 * this.props.level;
        const glyphStyle = {
            marginLeft: indent + "px",
            marginRight: "5px"
        }
        const { assets } = this.props;
        const level = this.props.level + 1;

        if (isEmpty(assets)) {
            return this.renderSingleElement("book", glyphStyle);
        } else {
            return (
                <div>
                    {this.renderSingleElement(this.state.open ? "menu-down" : "menu-right", glyphStyle)}
                    <Collapse in={this.state.open}>
                        <div>
                            {
                                Object.keys(assets).map((key, index) => (
                                    <ConnectedMenuElement
                                        name={assets[key].name}
                                        key={key}
                                        path={key}
                                        level={level}
                                        assets={assets[key].assets}
                                    />
                                ))
                            }
                        </div>
                    </Collapse>
                </div>
            );
        }
    }
}

const mapStateToProps = state => {
    return {
        asset: state.selectedAsset,
        searchResults: state.searchResults
    }
}

const mapDispatchToProps = dispatch => {
    return {
        selectAsset: asset => {
            dispatch(selectAsset(asset))
        }
    }
}

const ConnectedMenuElement = connect(
    mapStateToProps,
    mapDispatchToProps
)(MenuElement)

export default ConnectedMenuElement;
