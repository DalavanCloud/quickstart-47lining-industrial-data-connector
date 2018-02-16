import fetch from 'isomorphic-fetch'

import { store } from './index.js'

import { addNotification } from './app/actions.js'


const BACKEND_ERROR_CODES = [500];
const BACKEND_ERROR_MSG_KEYS = ['description', 'exception', 'message', 'traceback']


function dispatchDetailedNotification(json) {
    store.dispatch(
        addNotification(json, 'danger', true)
    )
}

function dispatchInternalServerErrorNotification() {
    store.dispatch(
        addNotification('Internal server error', 'danger')
    )
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



function getAfStructure() {
    return fetchWithBackendErrorHandling('/af-structure/view', {
        method: 'POST',
        credentials: 'include'
    });
}

function syncAfStructure() {
    return fetchWithBackendErrorHandling('/af-structure/sync', {
        method: 'POST',
        credentials: 'include'
    });
}

function subscribeToPiPoint(point) {
    var array = [point]
    return subscribeToPiPoints(array);
}

function subscribeToAllPiPoints() {
    return postJSON('pi-point/subscribe/all');
}

function subscribeToPiPoints(arrayOfPoints, all = false) {
    return postJSON('/pi-point/subscribe', arrayOfPoints);
}

function unsubscribeFromPiPoint(point) {
    var array = [point]
    return unsubscribeFromPiPoints(array);
}

function unsubscribeFromPiPoints(arrayOfPoints) {
    return postJSON('/pi-point/unsubscribe', arrayOfPoints);
}

function unsubscribeFromAllPiPoints() {
    return postJSON('/pi-point/unsubscribe/all');
}

function sendBackfillRequest(backfill) {
    return postJSON('/backfill', backfill);
}

function getSubscribedFeeds() {
    return fetchWithBackendErrorHandling('/pi-point/get-subscribed', {
        method: 'GET',
        credentials: 'include'
    }).then(
        response => {
            if (!response.ok) {
                store.dispatch(addNotification('Server error, please try again', 'danger'));
                throw new Error('Server error');
            } else {
                return response.json();
            }
    });
}

function getRecentEvents(limit) {
    return postJSON('/events/get-recent', {limit: limit}).then(response => response.json())
}

function sendForm(url, formJsonData, successMessage, failureMessage) {
    return postJSON(url, formJsonData).then(
        response => {
            if (!response.ok) {
                store.dispatch(addNotification(failureMessage, 'danger'));
                throw new Error('Request failed');
            } else {
                store.dispatch(addNotification(successMessage, 'info'));
            }
        }
    );
}

function searchAfStructure(searchJson) {
    return postJSON('/af-structure/search', searchJson).then(response => {
        return response.json();
    });
}

function getPiPointsList() {
    return get('/pi-point/list').then(response => {
        return response.json();
    })
}

function syncPiPointsList() {
    return fetchWithBackendErrorHandling('/pi-point/sync', {
        method: 'POST',
        credentials: 'include'
    });
}

function get(url) {
    return fetchWithBackendErrorHandling(url, {
        method: "GET",
        credentials: 'include',
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).catch(err => console.log(err))

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

function logout(username, password) {
    return fetchWithBackendErrorHandling('/logout', {
        method: 'POST',
        credentials: 'include',
    });
}

function getRules() {
    return fetchWithBackendErrorHandling('/scheduler/rules', {
        method: 'GET',
        credentials: 'include',
    }).then(response => response.json());
}

function getRule(ruleName) {
    return fetchWithBackendErrorHandling('/scheduler/rule/' + ruleName, {
        method: 'GET',
        credentials: 'include',
    }).then(response => response.json());
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
    getAfStructure,
    syncAfStructure,
    subscribeToPiPoint,
    subscribeToPiPoints,
    login,
    logout,
    sendForm,
    getSubscribedFeeds,
    sendBackfillRequest,
    searchAfStructure,
    getPiPointsList,
    unsubscribeFromPiPoint,
    unsubscribeFromPiPoints,
    getRecentEvents,
    checkIfLoggedIn,
    getRules,
    getRule,
    syncPiPointsList,
    getAthenaInfo,
    unsubscribeFromAllPiPoints,
    subscribeToAllPiPoints
};

export default Client;
