import { settings } from './views/Settings/reducer'
import { isLoggedIn } from './views/Login/reducer'
import { modal } from './Modal/reducer'
import { shouldReloadFeedList } from './views/FeedsList/reducer'


export const reducers = {
    settings,
    isLoggedIn,
    modal,
    shouldReloadFeedList
}
