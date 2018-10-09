package com.rean47lining.autobackfiller.dao;

import com.rean47lining.autobackfiller.model.Event;
import com.rean47lining.autobackfiller.utils.ConnectionService;
import org.apache.commons.dbutils.QueryRunner;

import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Timestamp;

public class EventDaoImpl implements EventDao {
    private ConnectionService connectionService;

    public EventDaoImpl(ConnectionService connectionService) {
        this.connectionService = connectionService;
    }

    @Override
    public int insertEvent(Event event) throws SQLException {
        try (Connection connection = connectionService.getConnection()){
            String insertSql = buildInsertQuery(event);
            QueryRunner queryRunner = new QueryRunner();
            return queryRunner.update(
                    connection,
                    insertSql,
                    event.getId(),
                    event.getType().toString(),
                    new Timestamp(event.getStart_timestamp().getMillis()),
                    new Timestamp(event.getUpdate_timestamp().getMillis()),
                    event.getStatus().toString(),
                    event.getName()
            );
        }
    }

    private String buildInsertQuery(Event event) {
        return "INSERT INTO event (id, type, start_timestamp, update_timestamp, status, name)" +
                " VALUES (?, ?, ?, ?, CAST(? AS eventstatus), ?)";
    }
}
