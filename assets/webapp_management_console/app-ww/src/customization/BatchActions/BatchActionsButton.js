import React from 'react'

import BatchActionsButton, {
    defaultSearchedActions,
    defaultSelectedActions
} from '../../shared/BatchActions/BatchActionsButton'
import Subscribe from './Subscribe'
import Unsubscribe from './Unsubscribe'

const selectedActions = [["Subscribe", Subscribe], ["Unsubscribe", Unsubscribe], ...defaultSelectedActions];
const searchedActions = [["Subscribe", Subscribe], ["Unsubscribe", Unsubscribe], ...defaultSearchedActions];


function CustomBatchActionsButton(props) {
    return <BatchActionsButton
        selectedActions={selectedActions}
        searchedActions={searchedActions}
        {...props}
    />
}

export default CustomBatchActionsButton
