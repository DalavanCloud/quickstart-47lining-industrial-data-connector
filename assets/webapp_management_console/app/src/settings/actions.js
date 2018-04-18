import Client from '../ApiClient.js'

export const SET_SETTINGS = 'SET_SETTINGS'


export function loadSettings() {
    return dispatch => {
        return Client.getSettings().then(
            settings => dispatch(setSettings(settings))
        )
    };
}

export function setSettings(settings) {
    return {
        type: SET_SETTINGS,
        settings
    }
}
