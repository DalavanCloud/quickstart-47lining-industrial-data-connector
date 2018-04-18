import { SET_NUMBER_OF_RECENT_EVENTS, SET_RECENT_EVENTS } from './EventsLogActions.js'

export function numberOfRecentEvents(state = 10, action) {
    switch (action.type) {
        case SET_NUMBER_OF_RECENT_EVENTS:
            return action.number
        default:
            return state
    }
}

export function recentEvents(state = [], action) {
    switch (action.type) {
        case SET_RECENT_EVENTS:
            return action.events
        default:
            return state
    }
}
