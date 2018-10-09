import React from 'react'

import DataSourceLabel from "../DataSourceLabel/DataSourceLabel";

import SubscriptionStatusLabel from '../../shared/components/SubscriptionStatusLabel'

export const attributesHeaders = ['Name', 'Description', 'Category', 'Feed', 'UOM', 'Type', 'Status'];

export const assetAttributes = { 'name': 'Name', 'description': 'Description', 'category': 'Category', 'template': 'Template', 'path': 'Path' };

export const feedAttributes = { 'name': 'Name', 'description': 'Description', 'category': 'Category', 'feed': 'Feed', 'uom': 'UOM' };

export function createRowFromAttribute(attribute) {
    return ([
        <td>{attribute.name}</td>,
        <td>{attribute.description}</td>,
        <td>{attribute.categories && attribute.categories.map((category, i) => <p key={i}>{category}</p>)}</td>,
        <td>{attribute.feed}</td>,
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
        </div>,
        <div className="inner">
            <h3>Template</h3>
            <p>{asset.template}</p>
        </div>,
        <div className="inner">
            <h3>Categories</h3>
            {asset.categories && asset.categories.map((category, i) => <p key={i}>{category}</p>)}
        </div>
    ]);
}