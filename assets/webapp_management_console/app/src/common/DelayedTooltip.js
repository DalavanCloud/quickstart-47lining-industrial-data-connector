import React from 'react';
import { Tooltip, OverlayTrigger } from 'react-bootstrap';


export default function DelayedTooltip({id, tooltip, placement, delayShow, delayHide, children}) {
    return (
        <OverlayTrigger
            overlay={<Tooltip id={id}>{tooltip}</Tooltip>}
            placement={placement}
            delayShow={delayShow}
            delayHide={delayHide}
        >
            {children}
        </OverlayTrigger>
    );
}

DelayedTooltip.defaultProps = {
    placement: "top",
    delayShow: 200,
    delayHide: 200
}
