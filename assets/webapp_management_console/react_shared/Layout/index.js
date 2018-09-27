import React from 'react'
import { ToastContainer } from 'react-toastify'

import Modal from '../Modal'
import Header from '../views/Header'


export default function Layout({ children, Header }) {
    return (
        <div>
            <Header />
            <Modal />
            <ToastContainer autoClose={8000} pauseOnHover />
            {children}
        </div>
    );
}

Layout.defaultProps = {
    Header: Header
}
