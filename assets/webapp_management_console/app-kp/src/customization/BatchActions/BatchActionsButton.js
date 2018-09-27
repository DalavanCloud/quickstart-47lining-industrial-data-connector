import React from 'react'

import BatchActionsButton from '../../shared/BatchActions/BatchActionsButton'
import Subscribe from './Subscribe'
import Unsubscribe from './Unsubscribe'

const selectedActions = [["Subscribe", Subscribe], ["Unsubscribe", Unsubscribe]];
const searchedActions = [["Subscribe", Subscribe], ["Unsubscribe", Unsubscribe]];


function CustomBatchActionsButton(props) {
    return <BatchActionsButton
        selectedActions={selectedActions}
        searchedActions={searchedActions}
        {...props}
    />
}

export default CustomBatchActionsButton
