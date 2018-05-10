import React from 'react'
import { NavLink } from 'react-router-dom'


export default function MenuLink({ to, children, ...otherProps }) {
    return (
        <li className="item">
            <NavLink to={to} {...otherProps} activeClassName="active">
                {children}
            </NavLink>
        </li>
    )
}
