import React, { Component } from 'react'
import { Collapse } from 'react-bootstrap'


import MenuNode from '../components/MenuNode'


export default class SubMenu extends Component {
    constructor(...args) {
        super(...args);

        this.state = {
            nodes: null,
        };
    }

    componentDidMount() {
        const open = this.props.selectedNode.startsWith(this.props.path);
        if (open && !this.state.nodes) {
            this.loadChildrenNodes()
        }
    }

    componentWillReceiveProps(newProps) {
        const open = newProps.selectedNode.startsWith(this.props.path);
        if (open && !this.state.nodes) {
            this.loadChildrenNodes()
        }
    }

    loadChildrenNodes() {
        this.props.getNodeChildren(this.props.parentId).then(
            response => this.setState({nodes: response.assets})
        )
    }

    handleOpen = e => {
        if (!this.state.nodes) {
            this.loadChildrenNodes()
        }
        this.props.onNodeSelect(e, this.props.path)
    }

    render() {
        const open = this.props.selectedNode.startsWith(this.props.path);

        return (
            <div>
                <MenuNode
                    name={this.props.name}
                    open={open}
                    level={this.props.level}
                    isLeaf={this.props.isLeaf}
                    handleOpen={this.handleOpen}
                    active={this.props.selectedNode === this.props.path}
                    showSpinner={!this.props.isLeaf && open && this.state.nodes === null}
                />
                {!this.props.isLeaf && <Collapse in={open && this.state.nodes !== null}>
                    <div>
                        {
                            this.state.nodes && this.state.nodes.map(node => (
                                <SubMenu
                                    parentId={node.id}
                                    name={node.name}
                                    key={node.name}
                                    path={node.id}
                                    isLeaf={node.isLeaf}
                                    level={this.props.level+1}
                                    onNodeSelect={this.props.onNodeSelect}
                                    selectedNode={this.props.selectedNode}
                                    getNodeChildren={this.props.getNodeChildren}
                                />
                            ))
                        }
                    </div>
                </Collapse>}
            </div>
        );
    }
}

SubMenu.defaultProps = {
    selectedNode: ''
}
