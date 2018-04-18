import React, { Component, Fragment } from 'react';
import { DropdownButton, MenuItem } from 'react-bootstrap'

import Subscribe from '../BatchActions/Subscribe.js'
import Unsubscribe from '../BatchActions/Unsubscribe.js'
import Interpolate from '../BatchActions/Interpolate.js'
import Backfill from '../BatchActions/Backfill.js'

import { showModal } from '../app/actions.js'
import { connect } from 'react-redux'


class BatchActionsButtons extends Component {

    selectedActions = [
        ["Subscribe", Subscribe],
        ["Unsubscribe", Unsubscribe],
        ["Interpolate", Interpolate],
        ["Backfill", Backfill]
    ]

    searchedActions = [
        ["Subscribe", Subscribe],
        ["Unsubscribe", Unsubscribe],
        ["Interpolate", Interpolate],
        ["Backfill", Backfill]
    ]

    render() {
        const { getSelectedFeeds, showSelectedFeedsActions, showSearchedFeedsActions, disableSelectedFeedsActions } = this.props;

        return (
            <DropdownButton bsStyle="primary" title="Actions" id="actions-dropdown">

                {showSelectedFeedsActions && <Fragment>
                    <MenuItem header>Selected feeds</MenuItem>
                    {this.selectedActions.map(action => (
                        <MenuItem
                            key={`action-${action[0]}`}
                            disabled={disableSelectedFeedsActions}
                            onClick={() => this.props.dispatch(
                                showModal(...action, {feeds: getSelectedFeeds()})
                            )}
                        >
                            {action[0]}
                        </MenuItem>
                    ))}
                </Fragment>}


                {showSearchedFeedsActions && <Fragment>
                    {showSelectedFeedsActions && <MenuItem divider />}
                    <MenuItem header>Searched feeds</MenuItem>
                    {this.searchedActions.map(action => (
                        <MenuItem
                            key={`action-${action[0]}`}
                            onClick={() => this.props.dispatch(
                                showModal(
                                    ...action,
                                    {
                                        onlySearchedFeeds: true,
                                        searchPattern: this.props.searchPattern,
                                        searchForStatus: this.props.searchForStatus,
                                        filters: this.props.filters,
                                        feedsTotalCount: this.props.feedsTotalCount,
                                    }
                                )
                            )}
                        >
                            {action[0]}
                        </MenuItem>
                    ))}
                </Fragment>}
            </DropdownButton>
        )
    }
}

BatchActionsButtons.defaultProps = {
    showSelectedFeedsActions: true,
    showSearchedFeedsActions: true
}

const ConnectedBatchActionsButtons = connect()(BatchActionsButtons);
export default ConnectedBatchActionsButtons;
