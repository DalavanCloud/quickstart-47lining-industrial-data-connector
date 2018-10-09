import React, { Fragment } from 'react'

import AthenaLink from './AthenaLink'
import MenuLink from './MenuLink'

import { StructureIcon, FeedsIcon, EventsLogIcon } from '../../components/icons'


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
            <li className="item">
                <AthenaLink />
            </li>
        </Fragment>
    )
}
