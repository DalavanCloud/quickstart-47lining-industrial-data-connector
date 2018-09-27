package com.rean47lining.autobackfiller.utils;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;


public class ConnectionService {
    private final Properties props;
    private String uri;

    public ConnectionService(String userName, String password, String databaseName, String host, boolean supportSSL) {
        this.uri = String.format("jdbc:postgresql://%s/%s", host, databaseName);
        this.props = new Properties();
        props.setProperty("user", userName);
        props.setProperty("password", password);
        String sslEnabled = supportSSL ? "true" : "false";
        props.setProperty("ssl", sslEnabled);
    }

    public Connection getConnection() throws SQLException {
        String connectionUrl = uri;
        return DriverManager.getConnection(connectionUrl, props);
    }
}
