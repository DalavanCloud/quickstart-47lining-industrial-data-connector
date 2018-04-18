import React, { Component } from 'react'

import StatusLabel from '../../common/StatusLabel.js'
import Checkbox from '../../common/Checkbox.js'


export default class AttributesTableItem extends Component {

    render() {
        const { attribute, checked, handleToggleAttribute } = this.props;

        return (
            <tr>
                <td>
                    <Checkbox
                        id={`${attribute.id}-check`}
                        checked={checked}
                        onChange={handleToggleAttribute}
                    />
                </td>
                <td>{attribute.name}</td>
                <td>{attribute.description}</td>
                <td>{attribute.categories && attribute.categories.map((category, i) => <p key={i}>{category}</p>)}</td>
                <td>{attribute.pi_point}</td>
                <td>{attribute.type}</td>
                <td>{attribute.pi_point && <StatusLabel status={attribute.subscription_status} />}</td>
            </tr>
        );
    }
}
