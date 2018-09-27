import React from 'react'

import AttributesTableItem from './AttributesTableItem'
import Checkbox from '../../components/Checkbox'


export default function AttributesTable({ assetId, isSelectAll, attributes, selectedAttributesIds, handleToggleAttribute, handleToggleAll, attributesHeaders, createRowFromAttribute }) {
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
                    {
                        attributesHeaders.map(attrName =>
                            <th>{attrName}</th>
                        )
                    }
                </tr>
                {
                    attributes.map((attribute, index) => (
                        <AttributesTableItem
                            key={attribute.id}
                            attribute={attribute}
                            checked={selectedAttributesIds[index]}
                            handleToggleAttribute={() => handleToggleAttribute(index)}
                            createRowFromAttribute={createRowFromAttribute}
                        />
                    ))
                }
            </tbody>
        </table>
    );
}
