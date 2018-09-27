export const RELOAD_FEED_LIST = 'RELOAD_FEED_LIST'


export function reloadFeedList(shouldReload) {
    return {
        type: RELOAD_FEED_LIST,
        shouldReload
    }
}
