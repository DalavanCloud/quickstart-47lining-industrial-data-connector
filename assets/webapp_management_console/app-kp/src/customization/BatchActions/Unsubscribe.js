import React from 'react'

import Unsubscribe from '../../shared/BatchActions/Unsubscribe';
import { data_sources } from './DataSources';

function CustomSubscribe(props) {
    return <Unsubscribe
        data_sources={data_sources}
        showDataSources={false}
        {...props}
    />
}

export default CustomSubscribe
