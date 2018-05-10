export function getPayloadFromProps(props) {
    return {
        feeds: props.feeds,
        onlySearchedFeeds: props.onlySearchedFeeds,
        searchPattern: props.searchPattern,
        searchForStatus: props.searchForStatus,
        filters: props.filters
    }
}
