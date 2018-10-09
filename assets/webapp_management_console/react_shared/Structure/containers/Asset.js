import React, { Component } from 'react'
import { Set } from 'global'

import Asset from '../components/Asset'

export default class AssetContainer extends Component {

    constructor(props) {
        super(props);
        this.state = {
            attributes: null,
            selectedAttributesIds: []
        }
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.open && !this.state.attributes) {
            this.props.apiClient.getAssetAttributes(this.props.asset.id, this.props.filters).then(
                json => this.setState({
                    attributes: json.attributes,
                    selectedAttributesIds: Array(json.attributes.length).fill(false)
                }),
                err => console.error(err)
            )
        }
    }

    isSelectAll() {
        return this.state.selectedAttributesIds.reduce((prev, curr) => prev && curr, true)
    }

    getSelectedFeeds = () => {
        const { attributes, selectedAttributesIds } = this.state;
        if (attributes) {
            return Array.from(new Set(attributes.filter(
                (attr, id) => selectedAttributesIds[id] && attr.feed
            ).map(attr => attr.feed)));
        } else {
            return [];
        }
    }

    handleToggleAll = () => {
        this.setState({selectedAttributesIds: Array(this.state.attributes.length).fill(!this.isSelectAll())})
    }

    handleToggleAttribute = index => {
        let selectedAttributesIds = [...this.state.selectedAttributesIds]
        selectedAttributesIds[index] = !selectedAttributesIds[index]
        this.setState({selectedAttributesIds})
    }

    render() {
        const { asset, open, active, handleToggle, handleSelect, attributesHeaders, createRowFromAttribute, BatchActionsButton, createAssetBasicInfo } = this.props;

        return (
            <Asset
                asset={asset}
                open={open}
                active={active}
                isSelectAll={this.isSelectAll()}
                getSelectedFeeds={this.getSelectedFeeds}
                disableSelectedFeedsActions={!this.state.selectedAttributesIds.reduce((prev, curr) => prev || curr, false)}
                handleToggle={handleToggle}
                handleSelect={handleSelect}
                attributes={this.state.attributes}
                selectedAttributesIds={this.state.selectedAttributesIds}
                handleToggleAttribute={this.handleToggleAttribute}
                handleToggleAll={this.handleToggleAll}
                attributesHeaders={attributesHeaders}
                createRowFromAttribute={createRowFromAttribute}
                BatchActionsButton={BatchActionsButton}
                createAssetBasicInfo={createAssetBasicInfo}
            />
        )
    }
}
