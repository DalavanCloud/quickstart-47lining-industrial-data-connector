import React, { Component } from 'react'
import { connect } from 'react-redux'

import { showModal } from '../../../Modal/actions'
import AddUserModal from './AddUserModal'


class AddUserButton extends Component {

    showModal = () => this.props.showModal(
        "Add user",
        AddUserModal,
        {addUserHandler: this.props.addUserHandler}
    )

    render() {
        return (
            <button
                style={{marginTop: "10px"}}
                className="btn btn-basic"
                onClick={this.showModal}
            >
                Add user
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
)(AddUserButton)
