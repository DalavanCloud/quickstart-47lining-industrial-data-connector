import { SET_SETTINGS } from './actions'


export function settings(state = {}, action) {
    switch (action.type) {
        case SET_SETTINGS:
            return action.settings
        default:
            return state
    }
}
