import React from 'react'
import { PulseLoader } from 'halogenium'

export default function Loading() {
    const color = "#DDD";
    return (
        <div style={{color: color, fontSize: "45px", fontWeight: "bold"}}>
            Loading <PulseLoader style={{display: "inline"}} color={color} />
        </div>
    );
}
