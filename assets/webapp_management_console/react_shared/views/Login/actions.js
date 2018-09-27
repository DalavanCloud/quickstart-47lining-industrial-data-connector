export const LOGGED_IN = 'LOGGED_IN'

export function setIsLoggedIn(isLoggedIn) {
    return {
        type: LOGGED_IN,
        isLoggedIn
    }
}
