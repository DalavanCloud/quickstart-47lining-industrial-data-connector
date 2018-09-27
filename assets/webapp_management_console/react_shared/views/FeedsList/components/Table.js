import React from 'react'

import Checkbox from '../../../components/Checkbox'
import { formatTimestamp } from '../../../utils'
import SubscriptionStatusLabel from '../../../components/SubscriptionStatusLabel'



function Row({ row, index, selectedIds, handleToggle, DataSourceLabel }) {
    return (
        <tr key={row.name}>
            <td>
                <Checkbox
                    id={row.name}
                    checked={selectedIds[index]}
                    onChange={() => handleToggle(index)}
                />
            </td>
            <td>{row.name}</td>
            <td>{formatTimestamp(row.update_timestamp)}</td>
            <td>
                <SubscriptionStatusLabel
                    status={row.subscription_status}
                    DataSourceLabel={DataSourceLabel}
                />
            </td>
        </tr>
    )
}


export default function Table({ rows, loading, isSelectAll, handleToggleAll, selectedIds, handleToggle , DataSourceLabel }) {
    return (
        <div className={`table-holder ${loading ? 'inactive' : ''}`}>
            <table className="checkbox-table">
                <tbody>
                    <tr>
                        <th>
                            <Checkbox
                                id="check-all"
                                checked={isSelectAll}
                                onChange={handleToggleAll}
                            />
                        </th>
                        <th>Name</th>
                        <th>Update timestamp</th>
                        <th>Status</th>
                    </tr>
                    {
                        rows.map((row, index) => (
                            <Row
                                key={row.name}
                                row={row}
                                index={index}
                                selectedIds={selectedIds}
                                handleToggle={handleToggle}
                                DataSourceLabel={DataSourceLabel}
                            />
                        ))
                    }
                </tbody>
            </table>
        </div>
    )
}
