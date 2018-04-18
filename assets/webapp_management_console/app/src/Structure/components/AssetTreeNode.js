import React from 'react'


export default function AssetTreeNode({ name, open, level, isLeaf, active, handleOpen, showSpinner }) {
    const glyphStyle = {
        marginLeft: 12 * level + "px",
        marginRight: "8px"
    }
    const glyph = isLeaf ? 'fa-folder' : open ? 'fa-caret-down' : 'fa-caret-right';
    return (
        <div className="list-group" onClick={handleOpen}>
            <a className={`list-group-item ${active ? "active" : ""}`}>
                <i style={glyphStyle} className={`fa ${glyph}`}></i>
                {name}
                {showSpinner && <i className="fa fa-spinner fa-spin pull-right" style={{fontSize: "1em", color: "rgb(0, 0, 0, 0.3)"}} aria-hidden="true"></i>}
            </a>
        </div>
    )
}

AssetTreeNode.defaultProps = {
    showSpinner: false
}
