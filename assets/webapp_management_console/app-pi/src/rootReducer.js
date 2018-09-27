import { combineReducers } from 'redux'

import { selectedAsset, searchResults, structureQueryString } from './shared/Structure/reducers'
import { reducers } from './shared/reducers'


const reducer = combineReducers({
    selectedAsset,
    searchResults,
    structureQueryString,
    ...reducers
})

export default reducer
