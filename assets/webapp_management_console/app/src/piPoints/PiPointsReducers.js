import { PI_POINTS_LIST } from './PiPointsActions.js'

export function piPointsList(state = [], action) {
    switch(action.type) {
        case PI_POINTS_LIST:
            return action.list;
        default:
            return state;
    }
}