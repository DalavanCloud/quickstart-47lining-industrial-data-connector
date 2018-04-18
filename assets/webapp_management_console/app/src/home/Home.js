import React from 'react'
import { Link } from 'react-router-dom'

import logo from '../resources/images/Logo_color.png'
import { StructureIcon } from '../common/icons.js'


function Home() {
    return (
        <div className="sub">
            <div className="form-box">
                <div className="text-center branding">
                    <img style={{width: '390px'}} src={logo} alt="logo" />
                </div>
                <form className="form-content">
                    <div className="text">
                        <p>Welcome to</p>
                        <h2>AWS Industrial Time Series Data Connector</h2>
                        <p>Management Console</p>
                    </div>
                    <Link to="/structure">
                        <button className="btn btn-primary console-btn" type="submit">
                            <StructureIcon /> <span>GO TO STRUCTURE</span>
                        </button>
                    </Link>
                </form>
            </div>
        </div>
    );
}

export default Home;
