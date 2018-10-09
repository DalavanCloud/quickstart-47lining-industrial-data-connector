package com.rean47lining.autobackfiller.services;

import com.amazonaws.services.sqs.AmazonSQS;
import com.google.common.collect.Lists;
import com.rean47lining.autobackfiller.dao.EventDao;
import com.rean47lining.autobackfiller.dao.FeedGroupDao;
import com.rean47lining.autobackfiller.exceptions.EventCreationException;
import com.rean47lining.autobackfiller.exceptions.FeedGroupCreationException;
import com.rean47lining.autobackfiller.model.*;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;

import java.sql.SQLException;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

public class AutobackfillerServiceImpl implements AutobackfillerService {
    private final AmazonSQS amazonSQSClient;
    private int interval;
    private List<Feed> feedList;
    private EventDao eventDao;
    private FeedGroupDao feedGroupDao;
    private String queueUrl;

    public AutobackfillerServiceImpl(String queueUrl, AmazonSQS amazonSQSClient, int interval, List<Feed> feedList,
                                     EventDao eventDao, FeedGroupDao feedGroupDao) {
        this.queueUrl = queueUrl;
        this.amazonSQSClient = amazonSQSClient;
        this.interval = interval;
        this.feedList = feedList;
        this.eventDao = eventDao;
        this.feedGroupDao = feedGroupDao;
    }

    @Override
    public void backfill(List<Status> statusList, DateTime beginWindow, DateTime endWindow) throws SQLException {
        int intervalMillis = (int)TimeUnit.MINUTES.toMillis(interval);
        int expectedStatuses = intervalMillis / (10 * 1000);
        int minStatuses = (int) Math.floor(expectedStatuses * 0.80); // we want at least 80% of expected statuses
        if(statusList.size() < minStatuses) {
            System.out.println(String.format("Expected at least %s statuses.", minStatuses));
            triggerBackfill(beginWindow, endWindow);
            return;
        }

        for (int i = 0; i < statusList.size() - 1; i++) {
            Status lhs = statusList.get(i);
            Status rhs = statusList.get(i + 1);

            int tresholdMillis = intervalMillis / 10; // We expect to receive status at least 10 times per interval
            if (isFailedSubwindow(lhs, rhs) || isUndetectedFailure(lhs, rhs, tresholdMillis)) {
                triggerBackfill(lhs.getTimestamp(), rhs.getTimestamp());
            }
        }
    }

    private boolean isFailedSubwindow(Status lhs, Status rhs) {
        boolean detected = lhs.getStatusType() != StatusType.RUNNING || rhs.getStatusType() != StatusType.RUNNING;
        if(detected)
            System.out.println(String.format("Failed subwindow detected: %s, %s", lhs, rhs));
        return detected;
    }

    private void triggerBackfill(DateTime lhs, DateTime rhs) throws SQLException {
        int chunkSize = 50;
        int chunkId = 0;
        for (List<Feed> feedChunk : Lists.partition(feedList, chunkSize)) {
            UUID uuid = UUID.randomUUID();
            BackfillRequest backfillRequest = BackfillRequest.createBackfillRequest(
                    lhs,
                    rhs,
                    uuid,
                    feedChunk.stream().map(Feed::getName).collect(Collectors.toList())
            );
            DateTime now = DateTime.now(DateTimeZone.UTC);
            Event event = new Event(uuid.toString(), Action.BACKFILL, now, now, EventStatus.PENDING, "Autobackfill");
            int inserted = eventDao.insertEvent(event);
            if (inserted != 1)
                throw new EventCreationException("Cannot insert event: " + event.toString());
            FeedGroup feedGroup = new FeedGroup(
                    chunkId,
                    uuid.toString(),
                    feedChunk.stream().map(Feed::getName).collect(Collectors.toList()),
                    "pending"
            );
            inserted = feedGroupDao.insertFeedGroup(feedGroup);
            if (inserted != 1)
                throw new FeedGroupCreationException("Cannot insert feed group: " + feedGroup.toString());
            amazonSQSClient.sendMessage(queueUrl, backfillRequest.toChunkJson(chunkId));
            chunkId++;
        }
    }

    private boolean isUndetectedFailure(Status lhs, Status rhs, int tresholdMillis) {
        boolean detected = lhs.getStatusType() == StatusType.RUNNING
                && rhs.getStatusType() == StatusType.RUNNING
                && (rhs.getTimestamp().getMillis() - lhs.getTimestamp().getMillis()) > tresholdMillis;
        if(detected)
            System.out.println(String.format("Failed subwindow detected: %s, %s, threshold: %d", lhs, rhs, tresholdMillis));
        return detected;
    }
}