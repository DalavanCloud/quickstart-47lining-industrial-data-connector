import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'

import { showConfirmActionModal } from '../../../Modal/actions'


class DeleteUserButton extends Component {

    showModal = () => this.props.showConfirmActionModal({
        title: "Delete user",
        paragraphsWithDescription: [<Fragment key="0">
            {'User '}
            <strong>{this.props.username}</strong>
            {' will be deleted. Continue?'}
        </Fragment>],
        confirmActionCallback: this.props.deleteUserHandler
    })

    render() {
        return (
            <button
                className="btn btn-danger"
                onClick={this.showModal}
                title={`Delete user ${this.props.username}`}
            >
                <i className='fa fa-remove'></i>
            </button>
        )
    }
}

const mapDispatchToProps = dispatch => {
    return {
        showConfirmActionModal: (...args) => {
            dispatch(showConfirmActionModal(...args))
        }
    }
}

export default connect(
    undefined,
    mapDispatchToProps
)(DeleteUserButton)
