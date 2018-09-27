import React from 'react'

import DataSourceLabel from "../DataSourceLabel/DataSourceLabel";

import SubscriptionStatusLabel from '../../shared/components/SubscriptionStatusLabel'

export const attributesHeaders = ['Name', 'Path' , 'Feed', 'Description', 'Type', 'Status'];

export const assetAttributes = { 'name': 'Name', 'path': 'Path' };

export const feedAttributes = { 'name': 'Name', 'description': 'Description', 'type': 'Type', 'path': 'Path' };

export function createRowFromAttribute(attribute) {
    return ([
        <td>{attribute.name}</td>,
        <td>{attribute.path}</td>,
        <td>{attribute.feed}</td>,
        <td>{attribute.description}</td>,
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

export function createAssetBasicInfo() {
    return ([]);
}