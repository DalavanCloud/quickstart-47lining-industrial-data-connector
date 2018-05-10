import React, { Component } from 'react'
import { Collapse } from 'react-bootstrap'

import Client from '../../ApiClient.js'


import AssetTreeNode from '../components/AssetTreeNode.js'


export default class AssetTreeSubtree extends Component {
    constructor(...args) {
        super(...args);

        this.state = {
            assets: null,
        };
    }

    componentDidMount() {
        const open = this.props.selectedAsset.startsWith(this.props.path);
        if (open && !this.state.assets) {
            this.loadChildrenAssets()
        }
    }

    componentWillReceiveProps(newProps) {
        const open = newProps.selectedAsset.startsWith(this.props.path);
        if (open && !this.state.assets) {
            this.loadChildrenAssets()
        }
    }

    loadChildrenAssets() {
        Client.getAssetChildren(this.props.parentId).then(
            assets => this.setState({assets})
        )
    }

    handleOpen = e => {
        if (!this.state.assets) {
            this.loadChildrenAssets()
        }
        this.props.onAssetSelect(e, this.props.path)
    }

    render() {
        const open = this.props.selectedAsset.startsWith(this.props.path);

        return (
            <div>
                <AssetTreeNode
                    name={this.props.name}
                    open={open}
                    level={this.props.level}
                    isLeaf={this.props.isLeaf}
                    handleOpen={this.handleOpen}
                    active={this.props.selectedAsset === this.props.path}
                    showSpinner={!this.props.isLeaf && open && this.state.assets === null}
                />
                {!this.props.isLeaf && <Collapse in={open && this.state.assets !== null}>
                    <div>
                        {
                            this.state.assets && this.state.assets.map(asset => (
                                <AssetTreeSubtree
                                    parentId={asset.id}
                                    name={asset.name}
                                    key={asset.name}
                                    path={asset.id}
                                    isLeaf={asset.isLeaf}
                                    level={this.props.level+1}
                                    onAssetSelect={this.props.onAssetSelect}
                                    selectedAsset={this.props.selectedAsset}
                                />
                            ))
                        }
                    </div>
                </Collapse>}
            </div>
        );
    }
}

AssetTreeSubtree.defaultProps = {
    selectedAsset: ''
}
