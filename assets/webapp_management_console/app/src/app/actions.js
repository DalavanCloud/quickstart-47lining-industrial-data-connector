export const ADD_NOTIFICATION = 'ADD_NOTIFICATION'
export const REMOVE_NOTIFICATION = 'REMOVE_NOTIFICATION'
export const SHOW_MODAL = 'SHOW_MODAL'
export const CLOSE_MODAL = 'CLOSE_MODAL'

export function addNotification(message, level, detailed = false) {
    return {
        type: ADD_NOTIFICATION,
        message,
        level,
        detailed
    };
}

export function removeNotification(index) {
    return {
        type: REMOVE_NOTIFICATION,
        index
    };
}

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