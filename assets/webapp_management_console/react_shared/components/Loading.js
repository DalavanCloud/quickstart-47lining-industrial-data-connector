import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { setTimeout, clearTimeout } from 'global'


export default class Loading extends Component {
    constructor(props) {
        super(props);

        this.state = {
            loaded: false
        }
    }

    componentDidMount() {
        this.timer = setTimeout(() => this.setState({loaded: true}), this.props.timeout)
    }

    componentWillUnmount() {
        clearTimeout(this.timer);
    }

    render() {
        const { text, fontSize, color, style } = this.props;
        return (
            this.state.loaded && <div
                style={{
                    textAlign: "center",
                    color: color,
                    fontSize: fontSize,
                    fontWeight: "bold",
                    ...style
                }}
            >
                {text} <i className="fa fa-spinner fa-spin" aria-hidden="true"></i>
            </div>
        );
    }
}

Loading.propTypes = {
    text: PropTypes.string,
    fontSize: PropTypes.string,
    color: PropTypes.string,
    timeout: PropTypes.number,
    style: PropTypes.object
}

Loading.defaultProps = {
    text: "Loading",
    color: "#DDD",
    fontSize: "3em",
    timeout: 0,
    style: {}
}
