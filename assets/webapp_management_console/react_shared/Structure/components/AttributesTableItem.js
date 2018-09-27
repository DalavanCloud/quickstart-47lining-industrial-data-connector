import React, {Component} from 'react'
import Checkbox from '../../components/Checkbox'

export default class AttributesTableItem extends Component {

    render() {
        const { attribute, checked, handleToggleAttribute, createRowFromAttribute } = this.props;

        return (
            <tr>
                <td>
                    <Checkbox
                        id={`${attribute.id}-check`}
                        checked={checked}
                        onChange={handleToggleAttribute}
                    />
                </td>
                {
                    createRowFromAttribute(attribute)
                }
            </tr>
        );
    }
}
