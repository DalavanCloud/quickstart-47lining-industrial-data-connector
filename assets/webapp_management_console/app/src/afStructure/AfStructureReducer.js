import { SELECT_ASSET, LOAD_DATA, SEARCH_RESULTS, CHANGE_ATTRIBUTES } from './AfStructureActions.js'


export function selectedAsset(state = '', action) {
    switch (action.type) {
        case SELECT_ASSET:
            return action.asset
        default:
            return state
    }
}

const afDataDefaultState = { nodes: [], menu: {} }
export function afData(state = afDataDefaultState, action) {

    switch (action.type) {
        case LOAD_DATA:
            return { nodes: action.afData.nodes, menu: action.afData.menu }
        default:
            return state
    }
}

export function searchResults(state = {}, action) {
    switch (action.type) {
        case SEARCH_RESULTS:
            return action.results
        case CHANGE_ATTRIBUTES:
            var newState = {...state};
            var newAsset = undefined;
            if (action.newAttributes.length === 0) {
                delete newState[action.assetName];
            } else if (action.assetName in newState) {
                newAsset = {...newState[action.assetName]};
                newAsset.attributes = action.newAttributes;
                delete newState[action.assetName];
                newState[action.assetName] = newAsset
            } else {
                newAsset = {
                    name: action.assetName,
                    attributes: action.newAttributes
                }
                newState[action.assetName] = newAsset
            }
            return newState;
        default:
            return state
    }
}
