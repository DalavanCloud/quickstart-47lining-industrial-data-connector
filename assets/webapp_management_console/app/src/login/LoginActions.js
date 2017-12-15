export const LOGGED_IN = 'LOGGED_IN'

export function isLoggedIn(isLoggedIn) {
    return {
        type: LOGGED_IN,
        isLoggedIn
    }
}
