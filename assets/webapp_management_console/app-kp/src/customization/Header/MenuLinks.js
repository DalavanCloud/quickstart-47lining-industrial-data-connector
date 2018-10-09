import React, { Fragment } from 'react'

import AthenaLink from '../../shared/views/Header/AthenaLink'
import MenuLink from '../../shared/views/Header/MenuLink'

import { StructureIcon, FeedsIcon, EventsLogIcon, SchedulerIcon } from '../../shared/components/icons'


export default function MenuLinks({ structureQueryString }) {
    return (
        <Fragment>
            <MenuLink to={`/structure${structureQueryString !== '' ? `?${structureQueryString}` : ''}`}>
                <StructureIcon /> Structure
            </MenuLink>
            <MenuLink to="/feeds">
                <FeedsIcon /> Feeds List
            </MenuLink>
            <MenuLink to="/events">
                <EventsLogIcon /> Events log
            </MenuLink>
            <MenuLink to="/view-rules">
                <SchedulerIcon /> Scheduler rules
            </MenuLink>
            <li className="item">
                <AthenaLink />
            </li>
        </Fragment>
    )
}
