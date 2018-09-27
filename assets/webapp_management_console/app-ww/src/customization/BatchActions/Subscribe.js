import React from 'react'

import Subscribe from '../../shared/BatchActions/Subscribe';
import { data_sources } from './DataSources';

function CustomSubscribe(props) {
    return <Subscribe
        data_sources={data_sources}
        showDataSources={false}
        {...props}
    />
}

export default CustomSubscribe
