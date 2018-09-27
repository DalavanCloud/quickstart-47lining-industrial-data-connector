export const SELECT_ASSET = 'SELECT_ASSET'
export const SEARCH_RESULTS = 'SEARCH_RESULTS'
export const SET_QUERY_STRING = 'SET_QUERY_STRING'

export function selectAsset(asset) {
    return {
        type: SELECT_ASSET,
        asset
    }
}

export function searchResults(results) {
    return {
        type: SEARCH_RESULTS,
        results
    }
}

export function setQueryString(queryString) {
    return {
        type: SET_QUERY_STRING,
        queryString
    }
}
