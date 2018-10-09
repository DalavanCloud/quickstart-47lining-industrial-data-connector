package com.rean47lining.autobackfiller;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.events.ScheduledEvent;
import com.amazonaws.services.sqs.AmazonSQSClientBuilder;
import com.rean47lining.autobackfiller.dao.*;
import com.rean47lining.autobackfiller.model.Feed;
import com.rean47lining.autobackfiller.model.Status;
import com.rean47lining.autobackfiller.services.AutobackfillerService;
import com.rean47lining.autobackfiller.services.AutobackfillerServiceImpl;
import com.rean47lining.autobackfiller.utils.ConnectionService;
import com.rean47lining.autobackfiller.utils.ElasticsearchResultSet;
import org.joda.time.DateTime;

import java.io.IOException;
import java.sql.SQLException;
import java.util.List;

public class Backfiller {

    private StatusDao statusDao = new StatusDaoImpl();

    public String handler(ScheduledEvent event, Context context) throws IOException, SQLException {
        int interval = Integer.valueOf(System.getenv("AUTOBACKFILL_PERIOD_MINUTES"));
        String queueUrl = System.getenv("QUEUE_URL");
        String feedTableName = System.getenv("FEED_TABLE_NAME");
        String dbUsername = System.getenv("DB_USERNAME");
        String dbPassword = System.getenv("DB_PASSWORD");
        String dbName = System.getenv("DB_NAME");
        String dbHost = System.getenv("DB_HOST");

        LambdaLogger logger = context.getLogger();
        ConnectionService connectionService = new ConnectionService(dbUsername, dbPassword, dbName, dbHost, false);
        FeedsDao feedsDao = new FeedsDaoImpl(connectionService, feedTableName);
        EventDao eventDao = new EventDaoImpl(connectionService);
        FeedGroupDao feedGroupDao = new FeedGroupDaoImpl(connectionService);

        List<Feed> feedList = feedsDao.getSubscribedFeeds();

        AutobackfillerService autobackfiller =
                new AutobackfillerServiceImpl(queueUrl, AmazonSQSClientBuilder.defaultClient(), interval,
                        feedList, eventDao, feedGroupDao);

        DateTime now = DateTime.now();
        DateTime previous = now.minusMinutes(interval);
        ElasticsearchResultSet statusesFromTimeRange = statusDao.getStatusesFromTimeRange(previous, now);

        for(List<Status> statusList: statusesFromTimeRange) {
            logger.log(String.format("Attempting backfill from: %s to %s, following statuses: %s", previous, now,
                    statusList));
            autobackfiller.backfill(statusList, previous, now);
        }

        return "OK";
    }
}