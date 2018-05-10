import React, { Component, Fragment } from 'react'
import UltimatePagination from 'react-ultimate-pagination-bootstrap-4'

import SizePerPage from './SizePerPage.js'

import StatusLabel from '../common/StatusLabel.js'
import Checkbox from '../common/Checkbox.js'

import { formatTimestamp } from '../utils.js'


class Table extends Component {

    renderRow(row, index) {
        return (
            <tr key={row.pi_point}>
                <td>
                    <Checkbox
                        id={row.pi_point}
                        checked={this.props.selectedIds[index]}
                        onChange={() => this.props.handleToggle(index)}
                    />
                </td>
                <td>{row.pi_point}</td>
                <td>{formatTimestamp(row.update_timestamp)}</td>
                <td><StatusLabel status={row.subscription_status} /></td>
            </tr>
        )
    }

    render() {
        return (
            <Fragment>
                <div className={`table-holder ${this.props.loading ? 'inactive' : ''}`}>
                    <table className="checkbox-table">
                        <tbody>
                            <tr>
                                <th>
                                    <Checkbox
                                        id="check-all"
                                        checked={this.props.isSelectAll}
                                        onChange={this.props.handleToggleAll}
                                    />
                                </th>
                                <th>Name</th>
                                <th>Update timestamp</th>
                                <th>Status</th>
                            </tr>
                            {
                                this.props.rows.map((row, index) => (
                                    this.renderRow(row, index)
                                ))
                            }
                        </tbody>
                    </table>
                </div>
                <div className="sub-nav">
                    <SizePerPage
                        sizePerPage={this.props.sizePerPage}
                        onSizePerPageChange={sizePerPage => this.props.onSizePerPageChange(sizePerPage)}
                    />
                    <nav aria-label="...">
                        <UltimatePagination
                            currentPage={this.props.activePage}
                            totalPages={Math.ceil(this.props.totalItemsCount / this.props.sizePerPage)}
                            onChange={page => this.props.onChange(page)}
                        />
                    </nav>
                </div>

            </Fragment>
        )
    }
}

export default Table;
