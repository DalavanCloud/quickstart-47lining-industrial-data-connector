import React from 'react'
import { Panel } from 'react-bootstrap'

import AttributesTable from './AttributesTable.js'
import BatchActionsButton from '../../BatchActions/BatchActionsButton.js'

import { ArrowRightIcon } from '../../common/icons.js'

import Breadcrumbs from './Breadcrumbs.js'


export default function Asset({ asset, open, handleToggle, isSelectAll, getSelectedFeeds, disableSelectedFeedsActions, active, handleSelect, attributes, selectedAttributesIds, handleToggleAttribute, handleToggleAll }) {
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
                    <div className="inner">
                        <h3>Description</h3>
                        <p>{asset.description}</p>
                    </div>
                    <div className="inner">
                        <h3>Template</h3>
                        <p>{asset.template}</p>
                    </div>
                    <div className="inner">
                        <h3>Categories</h3>
                        {asset.categories && asset.categories.map((category, i) => <p key={i}>{category}</p>)}
                    </div>
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
                            />
                            : <p>Asset has no attributes</p>
                        : null}
                </Panel.Body>
            </Panel.Collapse>
        </Panel>
    );
    // return <p>aaa</p>
}
