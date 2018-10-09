import apiClient from '../../apiClient'

export const SET_SETTINGS = 'SET_SETTINGS'


export function loadSettings() {
    return dispatch => {
        return apiClient.getSettings().then(
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
