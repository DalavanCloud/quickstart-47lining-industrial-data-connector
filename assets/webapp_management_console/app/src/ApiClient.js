import fetch from 'isomorphic-fetch'
import { console } from 'global'
import { toast } from 'react-toastify'

const BACKEND_ERROR_CODES = [500];
const BACKEND_ERROR_MSG_KEYS = ['description', 'exception', 'message', 'traceback']


function dispatchDetailedNotification(json) {
    toast.error(`Server error: ${json.message}`)
    console.error(json)
}

function dispatchInternalServerErrorNotification() {
    toast.error('Internal server error')
}

function fetchWithBackendErrorHandling(...args) {
    return fetch(...args).then(response => {
        if (BACKEND_ERROR_CODES.includes(response.status)) {
            try {
                // try reading json from response
                response.json().then(json => {
                    if (BACKEND_ERROR_MSG_KEYS.reduce((agg, val) => agg & val in json, true)) {
                        // check if response contains message in expected format
                        dispatchDetailedNotification(json);
                    } else {
                        dispatchInternalServerErrorNotification();
                    }
                })
            } catch(err) {
                // response without json, so generic server error
                dispatchInternalServerErrorNotification();
            }
            throw new Error('Backend Error');
        } else {
            return response;
        }
    });
}

function getSettings() {
    return fetchWithBackendErrorHandling('/settings', {
        method: 'GET',
        credentials: 'include'
    }).then(response => response.json());
}

function saveSettings(settings) {
    return postJSON('/settings/save', settings);
}

function syncStructure() {
    return fetchWithBackendErrorHandling('/structure/sync', {
        method: 'POST',
        credentials: 'include'
    });
}

function subscribeToFeeds(payload) {
    return postJSON('/subscribe', payload).then(
        () => toast.success('Subsription request sent'),
        () => toast.error('Cannot send subscription request')
    );
}

function interpolateFeeds(payload) {
    return postJSON('/interpolate', payload).then(
        () => toast.success('Interpolation request sent'),
        () => toast.error('Cannot send inteprolation request')
    );
}

function backfillFeeds(payload) {
    return postJSON('/backfill', payload).then(
        () => toast.success('Backfill request sent'),
        () => toast.error('Cannot send backfill request')
    );
}

function unsubscribeFromFeeds(payload) {
    return postJSON('/unsubscribe', payload).then(
        () => toast.success('Unsubsribe request sent'),
        () => toast.error('Cannot send unsubscribe request')
    );
}

function getRecentEvents(limit) {
    return postJSON('/events/get-recent', {limit: limit}).then(response => response.json())
}

function sendForm(url, formJsonData, successMessage, failureMessage) {
    const toastId = toast.warning('Your request is being processed, please wait', {autoClose: false});

    return postJSON(url, formJsonData).then(
        response => {
            if (!response.ok) {
                toast.update(toastId, {
                    render: failureMessage,
                    type: toast.TYPE.ERROR,
                    autoClose: 8000
                });
                throw new Error('Request failed');
            } else {
                toast.update(toastId, {
                    render: successMessage,
                    type: toast.TYPE.SUCCESS,
                    autoClose: 8000
                });
            }
        }
    );
}

function getAssetChildren(parentAssetId) {
    return postJSON('/structure/asset-children', {parentAssetId}).then(response => {
        return response.json();
    })
}

function searchAssets(filters = [], page, pageSize) {
    return postJSON('/structure/search', {filters, page: page-1, pageSize}).then(response => {
        return response.json();
    })
}

function getAssetAttributes(assetId, filters = []) {
    return postJSON('/structure/asset-attributes', {assetId, filters}).then(response => {
        return response.json();
    })
}

function searchFeedsList(page = 0, pageSize = 10, status = undefined, pattern = undefined, useRegex = false) {
    const payload = {
        page,
        page_size: pageSize,
        status,
        query: pattern,
        useRegex
    }
    return postJSON('/feeds/search', payload).then(response => {
        return response.json();
    })
}

function syncFeedsList() {
    return fetchWithBackendErrorHandling('/feeds/sync', {
        method: 'POST',
        credentials: 'include'
    });
}

function setSchedulerRule(ruleType, cron) {
    const url = `/scheduler/${ruleType}`;
    return postJSON(url, {cron});
}

function getSchedulerRules() {
    return get('/scheduler/rules').then(response => {
        return response.json();
    })
}

function get(url) {
    return fetchWithBackendErrorHandling(url, {
        method: "GET",
        credentials: 'include',
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).catch(err => console.error(err))

}

function postJSON(url, data = {}) {
    return fetchWithBackendErrorHandling(url, {
        method: 'POST',
        credentials: 'include',
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        },
        body: JSON.stringify(data)
    });
}

function checkIfLoggedIn() {
    return postJSON('/isloggedin', {}).then(response => {
        return response.json();
    });
}

function logout() {
    return fetchWithBackendErrorHandling('/logout', {
        method: 'POST',
        credentials: 'include',
    });
}

function getAthenaInfo() {
    return get('/athena-info').then(response => response.json());
}

function login(username, password) {
    return fetchWithBackendErrorHandling('/login', {
        method: 'POST',
        credentials: 'include',
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        },
        body: JSON.stringify({username: username, password: password})
    }).then(response => {
        return response.json();
    });
}


const Client = {
    syncStructure,
    subscribeToFeeds,
    login,
    logout,
    sendForm,
    unsubscribeFromFeeds,
    getRecentEvents,
    checkIfLoggedIn,
    syncFeedsList,
    getAthenaInfo,
    searchFeedsList,
    getAssetChildren,
    getSettings,
    saveSettings,
    searchAssets,
    getAssetAttributes,
    getSchedulerRules,
    setSchedulerRule,
    interpolateFeeds,
    backfillFeeds
};

export default Client;
