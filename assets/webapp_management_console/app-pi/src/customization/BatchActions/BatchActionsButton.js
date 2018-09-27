import React from 'react'

import BatchActionsButton, {
    defaultSearchedActions,
    defaultSelectedActions
} from '../../shared/BatchActions/BatchActionsButton'
import Interpolate from './Interpolate'
import Subscribe from './Subscribe'
import Unsubscribe from './Unsubscribe'

const selectedActions = [["Subscribe", Subscribe], ["Unsubscribe", Unsubscribe], ['Interpolate', Interpolate], ...defaultSelectedActions];
const searchedActions = [["Subscribe", Subscribe], ["Unsubscribe", Unsubscribe], ['Interpolate', Interpolate], ...defaultSearchedActions];


function CustomBatchActionsButton(props) {
    return <BatchActionsButton
        selectedActions={selectedActions}
        searchedActions={searchedActions}
        {...props}
    />
}

export default CustomBatchActionsButton
