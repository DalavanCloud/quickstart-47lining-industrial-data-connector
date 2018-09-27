import fetch from 'isomorphic-fetch'
import { console } from 'global'
import { toast } from 'react-toastify'

import { setIsLoggedIn } from './views/Login/actions'
import { store } from '../'


function dispatchDetailedNotification(json) {
    toast.error(`Server error: ${json.message}`)
    console.error(json)
}

function dispatchInternalServerErrorNotification() {
    toast.error('Internal server error')
}

function fetchWithBackendErrorHandling(url, params, auth = true) {

    if (auth) {
        if (!params.headers) params.headers = {};
        params.headers['access_token'] = sessionStorage.getItem('access_token');
        params.headers['refresh_token'] = sessionStorage.getItem('refresh_token');
        params.headers['id_token'] = sessionStorage.getItem('id_token');
        params.headers['username'] = sessionStorage.getItem('username');
    }

    return fetch(url, params).then(response => {
        if (response.status === 403) {
            toast.error('You are not logged in!');
            store.dispatch(setIsLoggedIn(false));
            return response;
        }
        else if (response.status === 401) {
            return response;
        }
        else if (!response.ok) {
            try {
                // try reading json from response
                response.json().then(json => {
                    if (Object.keys(json).includes('message')) {
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

export function get(url) {
    return fetchWithBackendErrorHandling(url, {
        method: "GET",
        credentials: 'include',
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
}

export function postJSON(url, data = {}) {
    return fetchWithBackendErrorHandling(url, {
        method: 'POST',
        credentials: 'include',
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        },
        body: JSON.stringify(data)
    });
}

export function sendForm(url, formJsonData, successMessage, failureMessage) {
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
        },
        () => toast.update(toastId, {
            render: failureMessage,
            type: toast.TYPE.ERROR,
            autoClose: 8000
        })
    );
}


const ApiClient = {
    getSettings: () => {
        return fetchWithBackendErrorHandling('/api/v1/settings/load', {
            method: 'GET',
            credentials: 'include'
        }).then(response => response.json());
    },
    saveSettings: settings => {
        return postJSON('/api/v1/settings/save', settings);
    },
    syncStructure: () => {
        return fetchWithBackendErrorHandling('/api/v1/structure/sync', {
            method: 'POST',
            credentials: 'include'
        });
    },
    subscribeToFeeds: payload => {
        return sendForm('/api/v1/feeds/subscribe', payload, 'Subscription request sent', 'Cannot send subscription request');
    },
    backfillFeeds: payload => {
        return sendForm('/api/v1/feeds/backfill', payload, 'Backfill request sent', 'Cannot send backfill request');
    },
    unsubscribeFromFeeds: payload => {
        return sendForm('/api/v1/feeds/unsubscribe', payload, 'Unsubsribe request sent', 'Cannot send unsubscribe request');
    },
    resetAllData: () => {
        return sendForm('/api/v1/feeds/reset', {"name": ""}, 'Unsubsribe request sent', 'Cannot send unsubscribe request');
    },
    getEvents: (type, status, from, to, page, sizePerPage) => {
        const payload = {
            page,
            page_size: sizePerPage,
            type,
            status,
            from,
            to
        }
        return postJSON(`/api/v1/events/list`, payload).then(response => {
            return response.json();
        })
    },
    getEventFeedGroups: (eventId, page, sizePerPage) => {
        const payload = {
            page,
            page_size: sizePerPage
        }
        return postJSON(`/api/v1/events/${eventId}`, payload).then(response => {
            return response.json();
        })
    },
    getAssetChildren: parentAssetId => {
        return postJSON('/api/v1/structure/asset-children', {parent_asset_id: parentAssetId}).then(response => {
            return response.json();
        })
    },
    searchAssets: (filters = [], page, pageSize) => {
        return postJSON('/api/v1/structure/search', {filters, page: page-1, page_size: pageSize}).then(response => {
            return response.json();
        })
    },
    getAssetAttributes: (assetId, filters = []) => {
        return postJSON('/api/v1/structure/asset-attributes', {asset_id: assetId, filters}).then(response => {
            return response.json();
        })
    },
    searchFeedsList: (page = 0, pageSize = 10, status = undefined, pattern = undefined, useRegex = false) => {
        const payload = {
            page,
            page_size: pageSize,
            status,
            query: pattern,
            use_regex: useRegex
        }
        return postJSON('/api/v1/feeds/search', payload).then(response => {
            return response.json();
        })
    },
    syncFeedsList: () => {
        return fetchWithBackendErrorHandling('/api/v1/feeds/sync', {
            method: 'POST',
            credentials: 'include'
        });
    },
    setSchedulerRule: (ruleType, cron) => {
        const url = `api/v1/scheduler/${ruleType}`;
        return postJSON(url, {cron});
    },
    getSchedulerRules: () => {
        return get('/api/v1/scheduler/rules').then(response => {
            return response.json();
        })
    },
    logout: () => {
        return fetchWithBackendErrorHandling('/logout', {
            method: 'POST',
            credentials: 'include',
        });
    },
    getAthenaInfo: () => {
        return get('/api/v1/athena/info').then(response => response.json());
    },
    login: (username, password) => {
        return fetchWithBackendErrorHandling('/api/v1/auth/login', {
            method: 'POST',
            credentials: 'include',
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            },
            body: JSON.stringify({ username, password })
        }, false).then(response => {
            return response.json();
        });
    },
    listUsers: () => {
        return postJSON('/api/v1/users/users', {}).then(response => response.json());
    },
    deleteUser: username => {
        return postJSON(`/api/v1/users/user/${username}/delete`);
    },
    registerUser: (username, firstName, lastName, password) => {
        return postJSON(
            '/api/v1/users/register',
            {
                username,
                first_name: firstName,
                last_name: lastName,
                password
            }
        );
    },
    editUser: (username, first_name, last_name) => {
        return postJSON(
            `/api/v1/users/user/${username}/update`,
            {
                first_name,
                last_name
            }
        )
    }
}

export default ApiClient
