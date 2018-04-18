import { combineReducers } from 'redux'
import { SHOW_MODAL, CLOSE_MODAL } from './actions.js'
import { selectedAsset, searchResults, structureQueryString } from '../Structure/reducers'
import { numberOfRecentEvents, recentEvents } from '../eventsLog/EventsLogReducer.js'
import { settings } from '../settings/reducer.js'

import { isLoggedIn } from '../login/LoginReducer.js'


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
    searchResults,
    numberOfRecentEvents,
    recentEvents,
    isLoggedIn,
    modal,
    settings,
    structureQueryString
})

export default reducer
