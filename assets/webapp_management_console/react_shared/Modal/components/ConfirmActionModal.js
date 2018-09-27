import React, { Component } from 'react'
import PropTypes from 'prop-types'


export default class ConfirmActionModal extends Component {

    handleConfirmActionClick = () => {
        this.props.confirmActionCallback();
        this.props.closeModalCallback();
    }

    render() {
        const {
            closeModalCallback,
            paragraphsWithDescription,
            confirmActionLabel,
            cancelActionLabel
        } = this.props;
        return (
            <div>
                {
                    paragraphsWithDescription.map(
                        (text, i) => <p key={`modal-description-${i}`}>{text}</p>
                    )
                }
                <button className="btn btn-primary" onClick={this.handleConfirmActionClick}>
                    {confirmActionLabel}
                </button>
                {' '}
                <button className="btn btn-secondary" onClick={closeModalCallback}>
                    {cancelActionLabel}
                </button>
            </div>
        )
    }
}

ConfirmActionModal.defaultProps = {
    confirmActionLabel: 'OK',
    cancelActionLabel: 'Cancel'
}

ConfirmActionModal.propTypes = {
    closeModalCallback: PropTypes.func.isRequired,
    confirmActionCallback: PropTypes.func.isRequired,
    paragraphsWithDescription: PropTypes.arrayOf(
        PropTypes.oneOfType([PropTypes.string, PropTypes.object])
    ).isRequired,
    confirmActionLabel: PropTypes.string,
    cancelActionLabel: PropTypes.string
}
