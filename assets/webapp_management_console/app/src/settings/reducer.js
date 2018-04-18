import { SET_SETTINGS } from './actions.js'


export function settings(state = {}, action) {
    switch (action.type) {
        case SET_SETTINGS:
            return action.settings
        default:
            return state
    }
}
