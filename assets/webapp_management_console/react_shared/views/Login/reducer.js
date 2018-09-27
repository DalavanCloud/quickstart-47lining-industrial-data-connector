import { LOGGED_IN } from './actions'

export function isLoggedIn(state = false, action) {
    switch(action.type) {
        case LOGGED_IN:
            return action.isLoggedIn;
        default:
            return state;
    }
}
