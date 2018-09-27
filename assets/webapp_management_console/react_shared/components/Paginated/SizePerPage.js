import React, { Component } from 'react';


export default class SizePerPage extends Component {

    handleChange(event) {
        event.preventDefault();
        this.props.onSizePerPageChange(event.target.value)
    }

    render() {
        const { options } = this.props;
        return (
            <div className="form-group select">
                <select
                    className="form-control"
                    id="show-last"
                    value={this.props.sizePerPage}
                    onChange={event => this.handleChange(event)}
                >
                    {
                        options.map(option => (
                            <option key={`option-${option}`} value={option}>{option}</option>
                        ))
                    }
                </select>
            </div>
        );
    }
}

SizePerPage.defaultProps = {
    options: [10, 100, 500, 1000]
};
