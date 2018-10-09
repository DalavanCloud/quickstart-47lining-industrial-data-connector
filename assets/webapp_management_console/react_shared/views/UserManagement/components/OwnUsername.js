import React from 'react'
import { Well } from 'react-bootstrap'


export default function OwnUsername({ username }) {
    return (
        <Well style={{fontWeight: "400"}}>
            You are logged in as <strong>{username}</strong>
        </Well>
    )
}
