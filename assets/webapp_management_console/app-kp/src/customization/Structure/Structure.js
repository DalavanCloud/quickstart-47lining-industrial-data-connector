import React from 'react'

import Structure from "../../shared/Structure";
import { attributesHeaders, assetAttributes, feedAttributes, createRowFromAttribute, createAssetBasicInfo } from './StructureConfig'
import BatchActionsButton from '../BatchActions/BatchActionsButton'
import apiClient from '../../apiClient'

export default function CustomStructure() {
    return <Structure
        attributesHeaders={attributesHeaders}
        assetAttributes={assetAttributes}
        feedAttributes={feedAttributes}
        createRowFromAttribute={createRowFromAttribute}
        BatchActionsButton={BatchActionsButton}
        createAssetBasicInfo={createAssetBasicInfo}
        apiClient={apiClient}
    />
}
