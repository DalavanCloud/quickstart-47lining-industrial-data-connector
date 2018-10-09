package com.rean47lining.autobackfiller.services;

import com.amazonaws.services.sqs.AmazonSQSClient;
import com.google.common.collect.ImmutableList;
import com.rean47lining.autobackfiller.dao.*;
import com.rean47lining.autobackfiller.model.*;
import org.joda.time.DateTime;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InOrder;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;

import java.sql.SQLException;
import java.util.List;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.times;
import static org.powermock.api.mockito.PowerMockito.mockStatic;
import static org.powermock.api.mockito.PowerMockito.when;

@RunWith(PowerMockRunner.class)
@PrepareForTest(AutobackfillerServiceImpl.class)
public class AutobackfillerServiceImplTest {
    private AutobackfillerServiceImpl autobackfillerService;
    private AmazonSQSClient amazonSQSClientMock;
    private String queueName = "test-queue";
    private EventDaoImpl eventDao;
    private FeedGroupDao feedGroupDao;

    @Before
    public void beforeEach() throws SQLException {
        amazonSQSClientMock = Mockito.mock(AmazonSQSClient.class);
        eventDao = Mockito.mock(EventDaoImpl.class);
        feedGroupDao = Mockito.mock(FeedGroupDao.class);
        UUID uuid = UUID.fromString("493410b3-dd0b-4b78-97bf-289f50f6e74f");
        mockStatic(UUID.class);
        when(UUID.randomUUID()).thenReturn(uuid);
        List<Feed> feedsMock = ImmutableList.of(new Feed(
                "sampleFeed",
                DateTime.now(),
                new SubscriptionStatus(SubscriptionStatusEnum.SUBSCRIBED, SubscriptionStatusEnum.UNSUBSCRIBED)));
        when(eventDao.insertEvent(any())).thenReturn(1);
        when(feedGroupDao.insertFeedGroup(any())).thenReturn(1);
        autobackfillerService = new AutobackfillerServiceImpl(
                queueName, amazonSQSClientMock, 1, feedsMock, eventDao, feedGroupDao
        );
    }

    @Test
    public void backfillTwoFills() throws SQLException {
        DateTime first = DateTime.now();
        Status status1 = new Status(StatusType.RUNNING, first);
        Status status2 = new Status(StatusType.FAILED, first.plusMinutes(1));
        Status status3 = new Status(StatusType.RUNNING, first.plusMinutes(2));
        List<Status> statusList = ImmutableList.of(status1, status2, status3);

        autobackfillerService.backfill(statusList, first, first.plusMinutes(3));

        InOrder inOrder = inOrder(amazonSQSClientMock, amazonSQSClientMock);
        inOrder.verify(amazonSQSClientMock, times(1)).sendMessage(queueName,
                BackfillRequest.createBackfillRequest(first, first.plusMinutes(3), UUID.randomUUID(),
                        ImmutableList.of("sampleFeed")).toChunkJson(0));
    }

    @Test
    public void backfillOneFills() throws SQLException {
        DateTime first = DateTime.now();
        Status status1 = new Status(StatusType.FAILED, first);
        Status status2 = new Status(StatusType.RUNNING, first.plusMinutes(1));
        Status status3 = new Status(StatusType.FAILED, first.plusMinutes(2));
        List<Status> statusList = ImmutableList.of(status1, status2, status3);

        autobackfillerService.backfill(statusList, first, first.plusMinutes(3));

        InOrder inOrder = inOrder(amazonSQSClientMock, amazonSQSClientMock);
        inOrder.verify(amazonSQSClientMock, times(1)).sendMessage(queueName,
                BackfillRequest.createBackfillRequest(first, first.plusMinutes(3), UUID.randomUUID(),
                        ImmutableList.of("sampleFeed")).toChunkJson(0));
    }

    @Test
    public void backfillConsecutiveMultipleRunning() throws SQLException {
        DateTime first = DateTime.now();
        Status status1 = new Status(StatusType.FAILED, first);
        Status status2 = new Status(StatusType.RUNNING, first.plusMinutes(1));
        Status status3 = new Status(StatusType.RUNNING, first.plusMinutes(2));
        Status status4 = new Status(StatusType.RUNNING, first.plusMinutes(3));
        Status status5 = new Status(StatusType.FAILED, first.plusMinutes(4));
        List<Status> statusList = ImmutableList.of(status1, status2, status3, status4, status5);

        autobackfillerService.backfill(statusList, first, first.plusMinutes(4));

        InOrder inOrder = inOrder(amazonSQSClientMock, amazonSQSClientMock);
        inOrder.verify(amazonSQSClientMock, times(1)).sendMessage(queueName,
                BackfillRequest.createBackfillRequest(first, first.plusMinutes(1), UUID.randomUUID(),
                        ImmutableList.of("sampleFeed")).toChunkJson(0));
        inOrder.verify(amazonSQSClientMock, times(1)).sendMessage(queueName,
                BackfillRequest.createBackfillRequest(first.plusMinutes(3),
                        first.plusMinutes(4), UUID.randomUUID(), ImmutableList.of("sampleFeed")).toChunkJson(0));
    }

    @Test
    public void backfillConsecutiveMultipleFailed() throws SQLException {
        DateTime first = DateTime.now();
        Status status1 = new Status(StatusType.RUNNING, first);
        Status status2 = new Status(StatusType.FAILED, first.plusMinutes(1));
        Status status3 = new Status(StatusType.FAILED, first.plusMinutes(2));
        Status status4 = new Status(StatusType.FAILED, first.plusMinutes(3));
        Status status5 = new Status(StatusType.RUNNING, first.plusMinutes(4));
        List<Status> statusList = ImmutableList.of(status1, status2, status3, status4, status5);

        autobackfillerService.backfill(statusList, first, first.plusMinutes(4));

        InOrder inOrder = inOrder(amazonSQSClientMock, amazonSQSClientMock);
        inOrder.verify(amazonSQSClientMock, times(1)).sendMessage(queueName,
                BackfillRequest.createBackfillRequest(first, first.plusMinutes(1), UUID.randomUUID(),
                        ImmutableList.of("sampleFeed")).toChunkJson(0));
        inOrder.verify(amazonSQSClientMock, times(1)).sendMessage(queueName,
                BackfillRequest.createBackfillRequest(first.plusMinutes(3),
                        first.plusMinutes(4), UUID.randomUUID(),
                        ImmutableList.of("sampleFeed")).toChunkJson(0));
    }

    @Test
    public void backfillOneStatus() throws SQLException {
        DateTime first = DateTime.now();
        Status status1 = new Status(StatusType.RUNNING, first);
        List<Status> statusList = ImmutableList.of(status1);

        autobackfillerService.backfill(statusList, first, first.plusMinutes(4));

        InOrder inOrder = inOrder(amazonSQSClientMock, amazonSQSClientMock);
        inOrder.verify(amazonSQSClientMock, times(1)).sendMessage(queueName,
                BackfillRequest.createBackfillRequest(first, first.plusMinutes(4), UUID.randomUUID(),
                        ImmutableList.of("sampleFeed")).toChunkJson(0));
    }

    @Test
    public void backfillNoStatus() throws SQLException {
        DateTime first = DateTime.now();
        List<Status> statusList = ImmutableList.of();

        autobackfillerService.backfill(statusList, first, first.plusMinutes(4));

        InOrder inOrder = inOrder(amazonSQSClientMock, amazonSQSClientMock);
        inOrder.verify(amazonSQSClientMock, times(1)).sendMessage(queueName,
                BackfillRequest.createBackfillRequest(first, first.plusMinutes(4), UUID.randomUUID(),
                        ImmutableList.of("sampleFeed")).toChunkJson(0));
    }
}