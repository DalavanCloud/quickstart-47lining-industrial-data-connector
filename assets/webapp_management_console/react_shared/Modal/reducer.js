import { SHOW_MODAL, CLOSE_MODAL } from './actions'


export function modal(state = {}, action) {
    switch (action.type) {
        case SHOW_MODAL:
            return {
                modalComponent: action.modalComponent,
                title: action.title,
                props: action.props
            }
        case CLOSE_MODAL:
            return {}
        default:
            return state;
    }
}
