import React, { Component } from 'react'
import { connect } from 'react-redux'

import { showModal } from '../../../Modal/actions'
import EditUserModal from './EditUserModal'


class EditUserButton extends Component {

    showModal = () => {
        const { editUserHandler, username, lastName, firstName } = this.props;
        return this.props.showModal(
            `Edit user ${username}`,
            EditUserModal,
            {
                editUserHandler,
                username,
                lastName,
                firstName
            }
        )
    }

    render() {
        return (
            <button
                className="btn btn-basic"
                onClick={this.showModal}
                title={`Edit user ${this.props.username}`}
            >
                <i style={{marginRight: "-2px", marginLeft: "-1px"}} className='fa fa-edit'></i>
            </button>
        )
    }
}

const mapDispatchToProps = dispatch => {
    return {
        showModal: (...args) => {
            dispatch(showModal(...args))
        }
    }
}

export default connect(
    undefined,
    mapDispatchToProps
)(EditUserButton)
