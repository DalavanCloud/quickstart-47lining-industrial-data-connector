import ConfirmActionModal from './components/ConfirmActionModal'

export const SHOW_MODAL = 'SHOW_MODAL'
export const CLOSE_MODAL = 'CLOSE_MODAL'


export function showModal(title, modalComponent, props = {}) {
    return {
        type: SHOW_MODAL,
        title,
        modalComponent,
        props
    }
}

export function closeModal() {
    return {
        type: CLOSE_MODAL
    }
}

export function showConfirmActionModal({
    title,
    paragraphsWithDescription,
    confirmActionLabel,
    cancelActionLabel,
    confirmActionCallback
}) {
    return showModal(
        title,
        ConfirmActionModal,
        {
            confirmActionCallback,
            paragraphsWithDescription,
            confirmActionLabel,
            cancelActionLabel
        }
    )
}
