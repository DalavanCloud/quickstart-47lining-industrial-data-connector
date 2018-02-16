export const SET_NUMBER_OF_RECENT_EVENTS_DAYS = 'SET_NUMBER_OF_RECENT_EVENTS_DAYS'
export const LOAD_RECENT_EVENTS = 'LOAD_RECENT_EVENTS'
export const SET_RECENT_EVENTS = 'SET_RECENT_EVENTS'


export function setNumberOfRecentEventsDays(number) {
    return {
        type: SET_NUMBER_OF_RECENT_EVENTS_DAYS,
        number
    }
}

export function setRecentEvents(events) {
    return {
        type: SET_RECENT_EVENTS,
        events
    }
}
