package com.rean47lining.autobackfiller.dao;

import com.rean47lining.autobackfiller.RDBSUtils;
import com.rean47lining.autobackfiller.model.Action;
import com.rean47lining.autobackfiller.model.Event;
import com.rean47lining.autobackfiller.model.EventStatus;
import com.rean47lining.autobackfiller.utils.ConnectionService;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import java.sql.SQLException;
import java.util.List;
import java.util.Map;

import static org.junit.Assert.assertEquals;

public class EventDaoImplTest {
    private EventDaoImpl eventDao;
    private static ConnectionService connectionService = new ConnectionService(
            "postgres",
            "postgres",
            "postgres",
            "localhost",
            false
    );

    private static RDBSUtils RDBSUtils = new RDBSUtils(connectionService);

    @BeforeClass
    public static void setUpBeforeAll() throws SQLException {
        RDBSUtils.createEventTable();
    }

    @AfterClass
    public static void tearDownAfterAll() throws SQLException {
        RDBSUtils.deleteEventTable();
    }

    @Before
    public void setUp() {
        eventDao = new EventDaoImpl(connectionService);
    }

    @Test
    public void insertEvent() throws SQLException {
        DateTime startTimestamp = DateTime.now(DateTimeZone.UTC);
        DateTime updateTimestamp = startTimestamp.plusMinutes(1);
        Event event = new Event("1", Action.BACKFILL, startTimestamp, updateTimestamp, EventStatus.SUCCESS, "Autobackfill");

        eventDao.insertEvent(event);
        List<Map<String, Object>> eventList = RDBSUtils.query("select * from event");

        assertEquals(1, eventList.size());
        Map<String, Object> eventResult = eventList.get(0);
        DateTime startTimestampResult = new DateTime(eventResult.get("start_timestamp"));
        DateTime updateTimestampResult = new DateTime(eventResult.get("update_timestamp"));
        assertEquals(startTimestamp.toDateTime(DateTimeZone.UTC), startTimestampResult.toDateTime(DateTimeZone.UTC));
        assertEquals(updateTimestamp.toDateTime(DateTimeZone.UTC), updateTimestampResult.toDateTime(DateTimeZone.UTC));
        assertEquals("1", eventResult.get("id"));
        assertEquals("backfill", eventResult.get("type"));
        assertEquals("success", eventResult.get("status"));
        assertEquals("Autobackfill", eventResult.get("name"));
    }
}