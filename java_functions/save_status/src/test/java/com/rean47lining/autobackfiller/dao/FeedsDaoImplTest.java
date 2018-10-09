package com.rean47lining.autobackfiller.dao;

import com.rean47lining.autobackfiller.RDBSUtils;
import com.rean47lining.autobackfiller.model.Feed;
import com.rean47lining.autobackfiller.model.SubscriptionStatus;
import com.rean47lining.autobackfiller.model.SubscriptionStatusEnum;
import com.rean47lining.autobackfiller.utils.ConnectionService;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.junit.*;

import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.List;

import static org.junit.Assert.assertEquals;

public class FeedsDaoImplTest {
    private FeedsDaoImpl feedsDao;
    private static ConnectionService connectionService = new ConnectionService(
            "postgres",
            "postgres",
            "postgres",
            "localhost",
            false
    );
    private static RDBSUtils rdbsUtils = new RDBSUtils(connectionService);

    @BeforeClass
    public static void setUpBeforeAll() throws SQLException {
        rdbsUtils.createFeedsTable();
    }

    @AfterClass
    public static void tearDownAfterAll() throws SQLException {
        rdbsUtils.deleteFeedsTable();
    }

    @Before
    public void setUp() {
        feedsDao = new FeedsDaoImpl(connectionService, "feed");
    }

    @After
    public void tearDown() throws SQLException {
        rdbsUtils.truncateFeedsTable();
    }

    @Test
    public void getFeeds() throws SQLException {
        DateTime now = DateTime.now(DateTimeZone.UTC);
        Timestamp timestamp = new Timestamp(now.getMillis());
        rdbsUtils.insert("INSERT INTO public.feed (name, subscription_status, update_timestamp) VALUES (?, (to_json(?::json)), ?)",
                "testName", "{\"archive\": \"unsubscribed\", \"snapshot\": \"unsubscribed\"}", timestamp);

        List<Feed> feeds = feedsDao.getFeeds(new SubscriptionStatus(SubscriptionStatusEnum.UNSUBSCRIBED, SubscriptionStatusEnum.UNSUBSCRIBED), "AND");

        assertEquals(1, feeds.size());
        Feed feed = feeds.get(0);
        assertEquals(new Feed("testName", now, new SubscriptionStatus(SubscriptionStatusEnum.UNSUBSCRIBED, SubscriptionStatusEnum.UNSUBSCRIBED)), feed);
    }

    @Test
    public void getSubscribedFeeds() throws SQLException {
        DateTime now = DateTime.now(DateTimeZone.UTC);
        Timestamp timestamp = new Timestamp(now.getMillis());
        rdbsUtils.insert("INSERT INTO public.feed (name, subscription_status, update_timestamp) VALUES (?, (to_json(?::json)), ?)",
                "testName", "{\"archive\": \"subscribed\", \"snapshot\": \"subscribed\"}", timestamp);
        rdbsUtils.insert("INSERT INTO public.feed (name, subscription_status, update_timestamp) VALUES (?, (to_json(?::json)), ?)",
                "testName", "{\"archive\": \"unsubscribed\", \"snapshot\": \"unsubscribed\"}", timestamp);

        List<Feed> feeds = feedsDao.getSubscribedFeeds();

        assertEquals(1, feeds.size());
        Feed feed = feeds.get(0);
        assertEquals(new Feed("testName", now, new SubscriptionStatus(SubscriptionStatusEnum.SUBSCRIBED, SubscriptionStatusEnum.SUBSCRIBED)), feed);
    }
}