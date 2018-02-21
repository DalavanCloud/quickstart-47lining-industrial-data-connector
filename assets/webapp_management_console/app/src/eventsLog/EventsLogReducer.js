import { SET_NUMBER_OF_RECENT_EVENTS_DAYS, SET_RECENT_EVENTS } from './EventsLogActions.js'

export function numberOfRecentEventsDays(state = 1, action) {
    switch (action.type) {
        case SET_NUMBER_OF_RECENT_EVENTS_DAYS:
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
