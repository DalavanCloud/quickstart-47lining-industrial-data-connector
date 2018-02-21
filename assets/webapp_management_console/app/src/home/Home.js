import React from 'react';
import { Grid, Col, Jumbotron } from 'react-bootstrap';


function Home() {
    return (
        <Grid>
            <Col sm={6} smOffset={3}>
                <Jumbotron>
                    <h2>Welcome to OSIsoft PI System to AWS Connector Management Console</h2>
                </Jumbotron>
            </Col>
        </Grid>
    );
}

export default Home;
