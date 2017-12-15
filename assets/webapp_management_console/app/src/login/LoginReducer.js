import { LOGGED_IN } from './LoginActions.js'

export function isLoggedIn(state = false, action) {
    switch(action.type) {
        case LOGGED_IN:
            return action.isLoggedIn;
        default:
            return state;
    }
}
