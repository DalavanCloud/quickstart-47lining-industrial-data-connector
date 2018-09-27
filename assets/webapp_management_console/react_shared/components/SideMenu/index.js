import React, { Component } from 'react'

import Loading from '../Loading'

import SubMenu from './containers/SubMenu'


class SideMenu extends Component {

    constructor(...args) {
        super(...args);

        this.state = {
            nodes: null
        };
    }

    componentDidMount() {
        this.props.getNodeChildren(null).then(
            response => this.setState({ nodes: response.assets })
        )
    }

    handleNodeSelect = (event, nodeId) => {
        event.stopPropagation();
        this.props.onNodeSelect(nodeId);
    }

    render() {
        const { nodes } = this.state;
        const level = 0;

        return nodes
            ? nodes.map(node => (
                <div
                    key={node.name}
                    className="list-group list-group-root well"
                >
                    <SubMenu
                        parentId={node.id}
                        name={node.name}
                        path={node.id}
                        isLeaf={node.isLeaf}
                        level={level}
                        onNodeSelect={this.handleNodeSelect}
                        selectedNode={this.props.selectedNode}
                        getNodeChildren={this.props.getNodeChildren}
                    />
                </div>
            ))
            : <Loading
                key="side-menu"
                timeout={3000}
                fontSize="2em"
            />
    }
}

export default SideMenu
