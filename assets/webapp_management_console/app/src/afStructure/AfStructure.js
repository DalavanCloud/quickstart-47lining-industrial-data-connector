import React, { Component } from 'react'
import { Grid, Row, Col, Button, ButtonGroup, Glyphicon, Jumbotron } from 'react-bootstrap'
import { connect } from 'react-redux'

import { loadData } from './AfStructureActions.js'
import { addNotification, showModal } from '../app/actions.js'

import Menu from './Menu.js';
import Content from './Content.js';
import Client from '../ApiClient.js'
import AfSearch from './AfSearch.js'
import { piPointList } from '../piPoints/PiPointsActions.js'
import Loading from '../app/Loading.js'


class AfStructure extends Component {
    constructor(props) {
        super(props);
        this.state = {
            asset: "",
            loading: true,
            loaded: false
        }
    }

    changeAsset(asset) {
        this.setState({ asset: asset });
    }

    componentDidMount() {
        Client.getAfStructure().then(
            response => {
                if (!response.ok) {
                    this.props.addNotification('Server error, please try again', 'danger');
                    throw new Error('Server error');
                } else {
                    return response.json();
                }
        }).then(
            json => {
                if (json === undefined || Object.getOwnPropertyNames(json).length === 0) {
                    this.props.addNotification('Cannot load AF structure data, please request sync', 'danger')
                    this.setState({loading: false, loaded: false})
                } else {
                    this.props.loadData(json);
                    this.setState({loading: false, loaded: true})
                }
        }).catch(err => console.log(err));
        Client.getPiPointsList().then(response => {
            this.props.loadPiPoints(response);
        }).catch(err => console.log(err));
    }

    handleAfStructureSync = () => {
        Client.syncAfStructure().then(response => {
            this.props.addNotification('Syncing request sent.', 'info')
        })
    }

    render() {
        return (
            <Grid style={{ textAlign: "left" }}>
                {this.state.loading ? <Loading /> :
                    this.state.loaded ?
                        [<Row key="A">
                            <Col md={3}>
                                <ButtonGroup vertical>
                                    <Button bsStyle='success' onClick={this.handleAfStructureSync}>
                                        Request AF structure sync <Glyphicon glyph="retweet" />
                                    </Button>
                                </ButtonGroup>
                            </Col>
                            <Col md={9}>
                                <AfSearch />
                            </Col>
                        </Row>,
                        <Row key="B">
                            <Col md={3}>
                                <Menu onClick={(asset) => this.changeAsset(asset)} />
                            </Col>
                            <Col md={9}>
                                <Content key={this.props.asset} asset={this.props.asset} />
                            </Col>
                        </Row>] :
                        <Jumbotron style={{textAlign: "center"}}>
                            <h2>There is no AF structure to display :(</h2>
                            <Button bsStyle='success' bsSize="large" onClick={this.handleAfStructureSync}>
                                Request AF structure sync <Glyphicon glyph="retweet" />
                            </Button>
                        </Jumbotron>
                }
            </Grid>
        );
    }

}

const mapStateToProps = state => {
    return {
        asset: state.selectedAsset
    }
}

const mapDispatchToProps = dispatch => {
    return {
        addNotification: (message, level) => {
            dispatch(addNotification(message, level));
        },
        loadData: json => {
            dispatch(loadData(json));
        },
        loadPiPoints: json => {
            dispatch(piPointList(json));
        },
        showModal: (title, component, props = {}) => {
            dispatch(showModal(title, component, props));
        }
    }
}

const ConnectedAfStructure = connect(
    mapStateToProps,
    mapDispatchToProps
)(AfStructure)

export default ConnectedAfStructure;
