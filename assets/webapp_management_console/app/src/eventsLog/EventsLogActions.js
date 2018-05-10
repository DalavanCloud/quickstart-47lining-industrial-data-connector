export const SET_NUMBER_OF_RECENT_EVENTS = 'SET_NUMBER_OF_RECENT_EVENTS'
export const LOAD_RECENT_EVENTS = 'LOAD_RECENT_EVENTS'
export const SET_RECENT_EVENTS = 'SET_RECENT_EVENTS'


export function setNumberOfRecentEvents(number) {
    return {
        type: SET_NUMBER_OF_RECENT_EVENTS,
        number
    }
}

export function setRecentEvents(events) {
    return {
        type: SET_RECENT_EVENTS,
        events
    }
}
