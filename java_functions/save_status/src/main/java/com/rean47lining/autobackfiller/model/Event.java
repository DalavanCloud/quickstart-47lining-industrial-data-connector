package com.rean47lining.autobackfiller.model;

import com.google.common.base.MoreObjects;
import org.joda.time.DateTime;

public class Event {
    private String id;
    private Action type;
    private DateTime start_timestamp;
    private DateTime update_timestamp;
    private EventStatus status;
    private String name;

    public Event(String id, Action type, DateTime startTimestamp, DateTime updateTimestamp, EventStatus status, String name) {
        this.id = id;
        this.type = type;
        this.start_timestamp = startTimestamp;
        this.update_timestamp = updateTimestamp;
        this.status = status;
        this.name = name;
    }

    public Event() {
    }

    public String getId() {
        return id;
    }

    public DateTime getStart_timestamp() {
        return start_timestamp;
    }

    public DateTime getUpdate_timestamp() {
        return update_timestamp;
    }

    public EventStatus getStatus() {
        return status;
    }

    public void setStatus(EventStatus status) {
        this.status = status;
    }

    public String getName() {
        return name;
    }

    public Action getType() {
        return type;
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("id", id)
                .add("type", type)
                .add("start_timestamp", start_timestamp)
                .add("update_timestamp", update_timestamp)
                .add("status", status)
                .toString();
    }
}
