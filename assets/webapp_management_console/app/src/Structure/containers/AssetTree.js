import React, { Component } from 'react'

import Client from '../../ApiClient.js'
import Loading from '../../app/Loading.js'

import AssetTreeSubtree from './AssetTreeSubtree.js'



class AssetTree extends Component {

    constructor(...args) {
        super(...args);

        this.state = {
            assets: null
        };
    }

    componentDidMount() {
        Client.getAssetChildren(null).then(
            assets => this.setState({assets})
        )
    }

    handleAssetSelect = (event, assetPath) => {
        event.stopPropagation();
        this.props.onAssetSelect(assetPath);
    }



    render() {
        const assets = this.state.assets;
        const level = 0;

        return assets
            ? assets.map(asset => (
                <div
                    key={asset.name}
                    className="list-group list-group-root well"
                >
                    <AssetTreeSubtree
                        parentId={asset.id}
                        name={asset.name}
                        path={asset.id}
                        isLeaf={asset.isLeaf}
                        level={level}
                        onAssetSelect={this.handleAssetSelect}
                        selectedAsset={this.props.selectedAsset}
                    />
                </div>
            ))
            : <Loading
                key="asset-tree"
                timeout={3000}
                fontSize="2em"
            />
    }
}

export default AssetTree
