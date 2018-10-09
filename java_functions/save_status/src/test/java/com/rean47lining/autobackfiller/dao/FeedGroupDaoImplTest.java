package com.rean47lining.autobackfiller.dao;

import com.google.common.collect.ImmutableList;
import com.rean47lining.autobackfiller.RDBSUtils;
import com.rean47lining.autobackfiller.model.FeedGroup;
import com.rean47lining.autobackfiller.utils.ConnectionService;
import org.junit.*;
import org.postgresql.jdbc.PgArray;

import java.sql.SQLException;
import java.util.List;
import java.util.Map;

import static org.junit.Assert.*;

public class FeedGroupDaoImplTest {
    private FeedGroupDaoImpl feedGroupDao;
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
        rdbsUtils.createEventTable();
        rdbsUtils.createFeedGroupTable();
    }

    @AfterClass
    public static void tearDownAfterAll() throws SQLException {
        rdbsUtils.deleteEventTable();
        rdbsUtils.deleteFeedGroupTable();
    }

    @Before
    public void setUp() {
        feedGroupDao = new FeedGroupDaoImpl(connectionService);
    }

    @After
    public void tearDown() throws SQLException {
        rdbsUtils.truncateFeedGroupTable();
        rdbsUtils.truncateEventTable();
    }

    @Test
    public void insertFeedGroup() throws SQLException {
        FeedGroup feedGroup = new FeedGroup(1, "event-id", ImmutableList.of("test-feed"), "success");
        rdbsUtils.insert("INSERT INTO public.event (id, type) VALUES (?, ?)", "event-id", "backfill");
        feedGroupDao.insertFeedGroup(feedGroup);

        List<Map<String, Object>> result = rdbsUtils.query("select * from feed_group");

        assertEquals(1, result.size());
        Map<String, Object> feedGroupResult = result.get(0);
        assertEquals(1, feedGroupResult.get("id"));
        assertEquals("event-id", feedGroupResult.get("event_id"));
        assertEquals("success", feedGroupResult.get("status"));
    }
}