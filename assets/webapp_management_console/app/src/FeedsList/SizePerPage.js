import React, { Component } from 'react';


class SizePerPage extends Component {

    handleChange(event) {
        event.preventDefault();
        this.props.onSizePerPageChange(event.target.value)
    }

    render() {
        return (
            <div className="form-group select">
                <select
                    className="form-control"
                    id="show-last"
                    value={this.props.sizePerPage}
                    onChange={event => this.handleChange(event)}
                >
                    <option value="10">10</option>
                    <option value="100">100</option>
                    <option value="500">500</option>
                    <option value="1000">1000</option>
                </select>
            </div>
        );
    }
}

export default SizePerPage;
