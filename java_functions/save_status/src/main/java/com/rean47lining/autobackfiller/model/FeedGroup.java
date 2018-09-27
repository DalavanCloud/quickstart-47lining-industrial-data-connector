package com.rean47lining.autobackfiller.model;

import java.util.List;

public class FeedGroup {
    private int id;
    private String eventId;
    private List<String> feeds;
    private String status;

    public FeedGroup(int id, String eventId, List<String> feeds, String status) {
        this.id = id;
        this.eventId = eventId;
        this.feeds = feeds;
        this.status = status;
    }

    public int getId() {
        return id;
    }

    public String getEventId() {
        return eventId;
    }

    public List<String> getFeeds() {
        return feeds;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}