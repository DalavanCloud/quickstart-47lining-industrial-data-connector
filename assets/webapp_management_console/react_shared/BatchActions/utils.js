import { getUtcDatetime } from '../utils'

export function getPayloadFromProps(props) {
    return {
        feeds: props.feeds,
        only_searched_feeds: props.onlySearchedFeeds,
        search_pattern: props.searchFeedsFilters && props.searchFeedsFilters.searchPattern,
        search_status: props.searchFeedsFilters && props.searchFeedsFilters.searchForStatus,
        use_regex: props.searchFeedsFilters && props.searchFeedsFilters.useRegex,
        filters: props.filters
    }
}

export function getDefaultEventName(eventType) {
    return `${eventType} ${getUtcDatetime()}`
}
