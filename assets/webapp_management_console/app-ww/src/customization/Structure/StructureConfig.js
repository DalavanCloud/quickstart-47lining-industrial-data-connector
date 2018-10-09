import React from 'react'

import DataSourceLabel from "../DataSourceLabel/DataSourceLabel";

import SubscriptionStatusLabel from '../../shared/components/SubscriptionStatusLabel'

export const attributesHeaders = ['Name', 'Feed', 'Description', 'UOM', 'Type', 'Status'];

export const assetAttributes = { 'name': 'Name', 'description': 'Description', 'path': 'Path' };

export const feedAttributes = { 'name': 'Name', 'description': 'Description', 'feed': 'Feed', 'uom': 'UOM' };

export function createRowFromAttribute(attribute) {
    return ([
        <td>{attribute.name}</td>,
        <td>{attribute.feed}</td>,
        <td>{attribute.description}</td>,
        <td>{attribute.uom}</td>,
        <td>{attribute.type}</td>,
        <td>
            {
                attribute.feed && attribute.subscription_status &&
                <SubscriptionStatusLabel
                    status={attribute.subscription_status}
                    DataSourceLabel={DataSourceLabel}
                />
            }
        </td>
    ]);
}

export function createAssetBasicInfo(asset) {
    return ([
        <div className="inner">
            <h3>Description</h3>
            <p>{asset.description}</p>
        </div>
    ]);
}