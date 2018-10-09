import { RELOAD_FEED_LIST } from './actions'


export function shouldReloadFeedList(state = false, action) {
    console.log(action);
    switch (action.type) {
        case RELOAD_FEED_LIST:
            return action.shouldReload
        default:
            return state
    }
}
