import React, { Component } from 'react'
import { Modal } from 'react-bootstrap'
import { connect } from 'react-redux'
import { closeModal } from './actions.js'

class ModalWindow extends Component {
    render() {
        const modal = this.props.modal;
        if (Object.getOwnPropertyNames(modal).length > 0) {
            const title = this.props.modal.title;
            const ModalComponent = this.props.modal.modalComponent;
            return (
                <Modal show onHide={() => this.props.closeModal()}>
                    <Modal.Header closeButton>
                        <Modal.Title>{title}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <ModalComponent {...modal.props} onSubmitCallback={() => this.props.closeModal()} />
                    </Modal.Body>
                </Modal>
            )
        } else return null;
    }
}

const mapStateToProps = state => {
    return {
        modal: state.modal
    }
}

const mapDispatchToProps = dispatch => {
    return {
        closeModal: () => {
            dispatch(closeModal());
        }
    }
}


const ConnectedModal = connect(
    mapStateToProps,
    mapDispatchToProps
)(ModalWindow);
export default ConnectedModal;
