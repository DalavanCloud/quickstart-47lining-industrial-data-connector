import React, {Component} from 'react'
import pluralize from 'pluralize'
import {Formik} from 'formik'
import {Button, Col, ControlLabel, Form, FormControl, FormGroup} from 'react-bootstrap'
import { connect } from 'react-redux'
import apiClient from '../apiClient.js'
import { getPayloadFromProps, getDefaultEventName } from './utils.js'
import { reloadFeedList } from '../views/FeedsList/actions'
import Loading from '../components/Loading'


class Subscribe extends Component {

    constructor(props) {
        super(props);
        this.state = {
            loading: false
        }
    }

    render() {
        const { feeds } = this.props;
        const totalCount = feeds ? feeds.length : this.props.feedsTotalCount;
        return (
            <div>
                <p>You are going to subscribe to {totalCount} {pluralize('feed', totalCount)}</p>
                {totalCount > 100 && <p>This operation can take a long time!</p>}
                <hr />
                <Formik
                    initialValues={{
                        name: '',
                        data_source: 'all'
                    }}
                    onSubmit={
                        values => {
                            this.setState({loading: true});
                            let payload = {...getPayloadFromProps(this.props), ...values}
                            apiClient.subscribeToFeeds(payload).then(() => {
                                this.props.reloadFeedList(true);
                                this.props.closeModalCallback();
                            });
                        }
                    }
                    render={props => (
                        <Form
                            onSubmit={props.handleSubmit}
                            horizontal
                        >
                            <FormGroup>
                                <Col componentClass={ControlLabel} sm={3}>
                                    Name
                                </Col>
                                <Col sm={9}>
                                    <FormControl
                                        type="text"
                                        name="name"
                                        value={props.values.name}
                                        placeholder={getDefaultEventName('subscribe')}
                                        onChange={props.handleChange}
                                    />
                                </Col>
                            </FormGroup>
                            {
                                this.props.showDataSources ?
                                    <FormGroup>
                                        <Col componentClass={ControlLabel} sm={3}>
                                            Data source
                                        </Col>
                                        <Col sm={9}>
                                            <select
                                                className="form-control"
                                                id="data_source"
                                                value={props.values.data_source}
                                                onChange={props.handleChange}
                                            >
                                                {Object.keys(this.props.data_sources).map(attr =>
                                                    <option value={attr}>{this.props.data_sources[attr]}</option>
                                                )}
                                            </select>
                                        </Col>
                                    </FormGroup> : null
                            }
                            <Button bsStyle="primary" onClick={props.handleSubmit}>
                                 {this.state.loading ? <Loading text='' fontSize='20px' /> : 'Continue'}
                            </Button>
                        </Form>
                    )}
                />
            </div>
        )
    }
}

Subscribe.defaultProps = {
    data_sources: {},
    showDataSources: true
}

const mapStateToProps = state => {
    return {
        shouldReloadFeedList: state.shouldReloadFeedList
    }
}


const mapDispatchToProps = dispatch => {
    return {
        reloadFeedList: (shouldReload) => {
            dispatch(reloadFeedList(shouldReload));
        }
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(Subscribe);
