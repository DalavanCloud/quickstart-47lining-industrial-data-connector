import thunkMiddleware from 'redux-thunk'
import { createStore, applyMiddleware, compose } from 'redux'

import React from 'react'
import ReactDOM from 'react-dom'
import { Provider } from 'react-redux'
import { BrowserRouter as Router } from 'react-router-dom'

import reducer from './rootReducer'

import App from './App'

import './shared/resources/styles/bootstrap.min.css'
import './shared/resources/styles/bootstrap-xl.css'
import './shared/resources/styles/main.css'


const middlewares = []
if (process.env.NODE_ENV === `development`) {
    const { logger } = require(`redux-logger`);
    middlewares.push(logger); // neat middleware that logs actions
}

middlewares.push(thunkMiddleware); // lets us dispatch() functions

const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
export const store = createStore(
    reducer,
    composeEnhancers(
        applyMiddleware(...middlewares)
    )
)

ReactDOM.render(
    <Provider store={store}>
        <Router>
            <App />
        </Router>
    </Provider>,
    document.getElementById('root')
);
