import React, { Component } from 'react'
import { connect } from 'react-redux'
import { ListGroup } from 'react-bootstrap'

import MenuElement from './MenuElement.js'


class Menu extends Component {

    render() {
        const assets = this.props.assets;
        var level = 0;
        return (
            <ListGroup className="menu" componentClass="ul">
                {
                    Object.keys(assets).map((key, index) => (
                        <MenuElement
                            name={assets[key].name}
                            key={key}
                            path={key}
                            level={level}
                            assets={assets[key].assets}
                        />
                    ))
                }
            </ListGroup>
        );
    }
}

const mapStateToProps = state => {
    return {
        asset: state.selectedAsset,
        assets: state.afData.menu,
        searchResults: state.searchResults
    }
}

const ConnectedMenu = connect(
    mapStateToProps
)(Menu)

export default ConnectedMenu;
