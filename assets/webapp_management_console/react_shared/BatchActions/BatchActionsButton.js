import React, {Component, Fragment} from 'react'
import {DropdownButton, MenuItem} from 'react-bootstrap'

import Backfill from '../BatchActions/Backfill'

import {showModal} from '../Modal/actions'
import {connect} from 'react-redux'


export const defaultSelectedActions = [
    ["Backfill", Backfill]
]

export const defaultSearchedActions = [
    ["Backfill", Backfill]
]

class BatchActionsButtons extends Component {

    render() {
        const { getSelectedFeeds, showSelectedFeedsActions, showSearchedFeedsActions, disableSelectedFeedsActions } = this.props;

        return (
            <DropdownButton bsStyle="primary" title="Actions" id="actions-dropdown">

                {showSelectedFeedsActions && <Fragment>
                    <MenuItem header>Selected feeds</MenuItem>
                    {this.props.selectedActions.map(action => (
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
                    {this.props.searchedActions.map(action => (
                        <MenuItem
                            key={`action-${action[0]}`}
                            onClick={() => this.props.dispatch(
                                showModal(
                                    ...action,
                                    {
                                        onlySearchedFeeds: true,
                                        searchFeedsFilters: this.props.searchFilters,
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
    showSearchedFeedsActions: true,
    selectedActions: defaultSelectedActions,
    searchedActions: defaultSearchedActions
}

const ConnectedBatchActionsButtons = connect()(BatchActionsButtons);
export default ConnectedBatchActionsButtons;
