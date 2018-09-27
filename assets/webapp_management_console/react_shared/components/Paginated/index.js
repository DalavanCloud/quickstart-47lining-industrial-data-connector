import React, { Component } from 'react'
import UltimatePagination from 'react-ultimate-pagination-bootstrap-4'

import SizePerPage from './SizePerPage.js'


export default class Paginated extends Component {
    state = {
        activePage: 1,
        sizePerPage: 10
    }

    handleSizePerPageChange = sizePerPage => {
        this.setState({sizePerPage, activePage: 1})
    }

    handlePageChange = activePage => {
        this.setState({activePage})
    }

    resetActivePage = () => {
        this.setState({activePage: 1})
    }

    renderPagination = totalItemsCount => (
        <div className="sub-nav">
            <SizePerPage
                sizePerPage={this.state.sizePerPage}
                onSizePerPageChange={this.handleSizePerPageChange}
            />
            <nav aria-label="...">
                <UltimatePagination
                    currentPage={this.state.activePage}
                    totalPages={Math.ceil(totalItemsCount / this.state.sizePerPage)}
                    onChange={this.handlePageChange}
                />
            </nav>
        </div>
    )

    render() {
        const { activePage, sizePerPage } = this.state;
        return this.props.render({
            activePage,
            sizePerPage,
            renderPagination: this.renderPagination,
            resetActivePage: this.resetActivePage
        })
    }
}

Paginated.defaultProps = {
    render: () => {},
}
