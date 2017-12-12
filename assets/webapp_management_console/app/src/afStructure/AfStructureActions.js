export const SELECT_ASSET = 'SELECT_ASSET'
export const LOAD_DATA = 'LOAD_DATA'
export const TOGGLE_ATTRIBUTE = 'TOGGLE_ATTRIBUTE'
export const CREATE_EXPAND_ATTRIBUTE_ARRAY = 'CREATE_EXPAND_ATTRIBUTE_ARRAY'
export const SUBSCRIBE_TO_PI_POINT = 'SUBSCRIBE_TO_PI_POINT'
export const SEARCH_RESULTS = 'SEARCH_RESULTS'
export const CHANGE_ATTRIBUTES = 'CHANGE_ATTRIBUTES'


export function selectAsset(asset) {
    return {
        type: SELECT_ASSET,
        asset
    }
}

export function loadData(afData) {
    return {
        type: LOAD_DATA,
        afData
    }
}

export function searchResults(results) {
    return {
        type: SEARCH_RESULTS,
        results
    }
}

export function changeAttributes(assetName, newAttributes) {
    return {
        type: CHANGE_ATTRIBUTES,
        assetName,
        newAttributes
    }
}