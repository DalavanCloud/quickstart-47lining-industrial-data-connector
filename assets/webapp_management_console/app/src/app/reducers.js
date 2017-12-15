import { combineReducers } from 'redux'
import { ADD_NOTIFICATION, REMOVE_NOTIFICATION, SHOW_MODAL, CLOSE_MODAL } from './actions.js'
import { selectedAsset, afData, searchResults } from '../afStructure/AfStructureReducer.js'
import { piPointsList } from '../piPoints/PiPointsReducers.js'
import { numberOfRecentEventsDays, recentEvents } from '../eventsLog/EventsLogReducer.js'

import { isLoggedIn } from '../login/LoginReducer.js'



function notifications(state = [], action) {
    switch (action.type) {
        case ADD_NOTIFICATION:
            return [
                ...state,
                {
                    message: action.message,
                    level: action.level,
                    detailed: action.detailed
                }
            ];

        case REMOVE_NOTIFICATION:
            return [
                ...state.slice(0, action.index),
                ...state.slice(action.index + 1)
            ];

        default:
            return state
    }
}

function modal(state = {}, action) {
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

const reducer = combineReducers({
    selectedAsset,
    afData,
    notifications,
    searchResults,
    piPointsList,
    numberOfRecentEventsDays,
    recentEvents,
    isLoggedIn,
    modal
})

export default reducer
