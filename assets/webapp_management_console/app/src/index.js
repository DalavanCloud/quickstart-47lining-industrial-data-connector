import thunkMiddleware from 'redux-thunk'
import { createStore, applyMiddleware, compose } from 'redux'

import React from 'react'
import ReactDOM from 'react-dom'
import { Provider } from 'react-redux'

import reducer from './app/reducers.js'

import './index.css'
import './bootstrap/css/bootstrap.css'
import App from './app/App'
import registerServiceWorker from './registerServiceWorker'


const middlewares = []
if (process.env.NODE_ENV === `development`) {
    const { logger } = require(`redux-logger`);
    middlewares.push(logger); // neat middleware that logs actions
}

middlewares.push(thunkMiddleware); // lets us dispatch() functions

const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
export const store = createStore(reducer,  composeEnhancers(
        applyMiddleware(...middlewares)
    )
)


ReactDOM.render(
    <Provider store={store}>
        <App />
    </Provider>,
    document.getElementById('root')
);

registerServiceWorker();
