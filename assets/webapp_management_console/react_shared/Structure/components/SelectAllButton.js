import React from 'react'
import { Button, ButtonGroup } from 'react-bootstrap'

export default function SelectAllButton({handleSelectAll, handleDeselectAll}) {
    return (
        <ButtonGroup className="pullright">
            <Button onClick={handleSelectAll}>Select all</Button>
            <Button onClick={handleDeselectAll}>Deselect all</Button>
        </ButtonGroup>
    )
}
