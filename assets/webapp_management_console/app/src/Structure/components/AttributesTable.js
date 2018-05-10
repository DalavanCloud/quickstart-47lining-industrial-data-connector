import React from 'react'

import AttributesTableItem from './AttributesTableItem.js'
import Checkbox from '../../common/Checkbox.js'


export default function AttributesTable({ assetId, isSelectAll, attributes, selectedAttributesIds, handleToggleAttribute, handleToggleAll }) {
    return (
        <table className="checkbox-table">
            <tbody>
                <tr>
                    <th>
                        <Checkbox
                            id={`${assetId}-check-all`}
                            checked={isSelectAll}
                            onChange={handleToggleAll}
                        />
                    </th>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Category</th>
                    <th>Feed</th>
                    <th>Type</th>
                    <th>Status</th>
                </tr>
                {
                    attributes.map((attribute, index) => (
                        <AttributesTableItem
                            key={attribute.id}
                            attribute={attribute}
                            checked={selectedAttributesIds[index]}
                            handleToggleAttribute={() => handleToggleAttribute(index)}
                        />
                    ))
                }
            </tbody>
        </table>
    );
}
