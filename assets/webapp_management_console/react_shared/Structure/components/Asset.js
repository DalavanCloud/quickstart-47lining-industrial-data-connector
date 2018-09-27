import React from 'react'
import { Panel } from 'react-bootstrap'

import AttributesTable from './AttributesTable'

import { ArrowRightIcon } from '../../components/icons'

import Breadcrumbs from './Breadcrumbs'


export default function Asset(
    {asset, open, handleToggle, isSelectAll, getSelectedFeeds, disableSelectedFeedsActions, active, handleSelect, attributes, selectedAttributesIds, handleToggleAttribute, handleToggleAll, attributesHeaders, createRowFromAttribute, BatchActionsButton, createAssetBasicInfo }) {
    return (
        <Panel className={active ? 'active' : ''} expanded={open && attributes !== null} onToggle={() => {}}>
            <Panel.Heading>
                <Panel.Title>
                    <div className="text">
                        <h2 className="title" onClick={() => handleSelect(asset.id)}>{asset.name}</h2>
                        <Breadcrumbs
                            assetId={asset.id}
                            handleSelect={handleSelect}
                        />
                    </div>
                    <BatchActionsButton
                        getSelectedFeeds={getSelectedFeeds}
                        disableSelectedFeedsActions={disableSelectedFeedsActions}
                        showSearchedFeedsActions={false}
                    />
                    <div
                        className="collapse-position"
                        onClick={handleToggle}
                    >
                        <ArrowRightIcon
                            className={open && !attributes ? "fa-spin"  : ""}
                            rotation={open && attributes ? -90 : 90}
                        />
                    </div>
                </Panel.Title>
                <div className="basic-info">
                    {
                        createAssetBasicInfo(asset)
                    }
                </div>
            </Panel.Heading>
            <Panel.Collapse>
                <Panel.Body>
                    {attributes
                        ? attributes.length > 0
                            ? <AttributesTable
                                assetId={asset.id}
                                isSelectAll={isSelectAll}
                                attributes={attributes}
                                selectedAttributesIds={selectedAttributesIds}
                                handleToggleAttribute={handleToggleAttribute}
                                handleToggleAll={handleToggleAll}
                                attributesHeaders={attributesHeaders}
                                createRowFromAttribute={createRowFromAttribute}
                            />
                            : <p>Asset has no attributes</p>
                        : null}
                </Panel.Body>
            </Panel.Collapse>
        </Panel>
    );
    // return <p>aaa</p>
}
