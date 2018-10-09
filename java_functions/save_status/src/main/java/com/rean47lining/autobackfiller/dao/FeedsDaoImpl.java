package com.rean47lining.autobackfiller.dao;

import com.rean47lining.autobackfiller.model.Feed;
import com.rean47lining.autobackfiller.model.SubscriptionStatus;
import com.rean47lining.autobackfiller.model.SubscriptionStatusEnum;
import com.rean47lining.autobackfiller.utils.ConnectionService;
import org.apache.commons.dbutils.QueryRunner;
import org.apache.commons.dbutils.handlers.MapListHandler;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.postgresql.util.PGobject;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class FeedsDaoImpl implements FeedsDao {
    private final String feedTableName;
    private ConnectionService connectionService;

    public FeedsDaoImpl(ConnectionService connectionService, String feedTableName) {
        this.connectionService = connectionService;
        this.feedTableName = feedTableName;
    }

    @Override
    public List<Feed> getFeeds(SubscriptionStatus subscriptionStatus, String operator) throws SQLException {
        String query = buildGetFeedsQuery(subscriptionStatus, operator);
        return getFeeds(query);
    }

    @Override
    public List<Feed> getSubscribedFeeds() throws SQLException {
        String query = buildGetFeedsQuery(
                new SubscriptionStatus(SubscriptionStatusEnum.SUBSCRIBED, SubscriptionStatusEnum.SUBSCRIBED),
                "OR"
        );
        return getFeeds(query);
    }

    private List<Feed> getFeeds(String query) throws SQLException {
        List<Feed> result = new ArrayList<>();
        QueryRunner runner = new QueryRunner();
        MapListHandler beanListHandler = new MapListHandler();

        try(Connection connection = connectionService.getConnection()) {
            List<Map<String, Object>> list = runner.query(connection, query, beanListHandler);
            for (Map<String, Object> object : list) {
                PGobject p = (PGobject)object.get("subscription_status");
                result.add(new Feed(
                        (String) object.get("name"),
                        new DateTime(object.get("update_timestamp")).toDateTime(DateTimeZone.UTC),
                        SubscriptionStatus.fromJson(p.getValue())
                ));
            }
        }
        return result;
    }

    private String buildGetFeedsQuery(SubscriptionStatus subscriptionStatus, String operator) {
        return String.format(
             "SELECT * FROM %s WHERE subscription_status ->> 'archive' = '%s' %s subscription_status ->> 'snapshot' = '%s'",
             feedTableName,
             subscriptionStatus.getArchive(),
             operator,
             subscriptionStatus.getSnapshot()
        );
    }
}
