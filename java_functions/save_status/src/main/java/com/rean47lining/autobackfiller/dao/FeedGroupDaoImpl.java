package com.rean47lining.autobackfiller.dao;

import com.rean47lining.autobackfiller.model.FeedGroup;
import com.rean47lining.autobackfiller.utils.ConnectionService;
import org.apache.commons.dbutils.QueryRunner;

import java.sql.Array;
import java.sql.Connection;
import java.sql.SQLException;

public class FeedGroupDaoImpl implements FeedGroupDao {
    private ConnectionService connectionService;

    public FeedGroupDaoImpl(ConnectionService connectionService) {
        this.connectionService = connectionService;
    }

    @Override
    public int insertFeedGroup(FeedGroup feedGroup) throws SQLException {
        try(Connection connection = connectionService.getConnection()) {
            QueryRunner queryRunner = new QueryRunner();
            String[] feedsStr = feedGroup.getFeeds().toArray(new String[feedGroup.getFeeds().size()]);
            Array feeds = connection.createArrayOf("text", feedsStr);
            String insertSql = "INSERT INTO feed_group (id, event_id, feeds, status)" +
                    " VALUES (?, ?, ?, CAST(? AS eventstatus))";
            return queryRunner.update(connection, insertSql, feedGroup.getId(), feedGroup.getEventId(), feeds,
                    feedGroup.getStatus());
        }
    }
}
