import {
    SELECT_ASSET, SEARCH_RESULTS, SET_QUERY_STRING
} from '../actions'



export function selectedAsset(state = '', action) {
    switch (action.type) {
        case SELECT_ASSET:
            return action.asset
        default:
            return state
    }
}

export function searchResults(state = {}, action) {
    switch (action.type) {
        case SEARCH_RESULTS:
            return action.results
        default:
            return state
    }
}

export function structureQueryString(state = '', action) {
    switch (action.type) {
        case SET_QUERY_STRING:
            return action.queryString
        default:
            return state
    }
}
