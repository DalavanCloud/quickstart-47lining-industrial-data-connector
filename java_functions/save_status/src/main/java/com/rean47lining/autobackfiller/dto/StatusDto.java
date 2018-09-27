package com.rean47lining.autobackfiller.dto;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.rean47lining.autobackfiller.model.Status;
import org.joda.time.format.DateTimeFormat;

import java.util.Date;

public class StatusDto {
    private String dateRangeKey; // format yyyy-MM-dd
    private Date datetime;
    private String status;

    public StatusDto() { }

    public StatusDto(Status status) {
        this.dateRangeKey = DateTimeFormat.forPattern("yyyy-MM-dd").print(status.getTimestamp());
        this.datetime = status.getTimestamp().toDate();
        this.status = status.getStatusType().name();
    }

    public String getDateRangeKey() {
        return dateRangeKey;
    }

    public void setDateRangeKey(String dateRangeKey) {
        this.dateRangeKey = dateRangeKey;
    }

    public Date getDatetime() {
        return datetime;
    }

    public void setDatetime(Date datetime) {
        this.datetime = datetime;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String toJson() {
        Gson gson = new GsonBuilder().setDateFormat("yyyy-MM-dd'T'HH:mm:ss").create();
        return gson.toJson(this);
    }

    public static StatusDto fromJson(String input) {
        Gson gson = new GsonBuilder().setDateFormat("yyyy-MM-dd'T'HH:mm:ss").create();
        return gson.fromJson(input, StatusDto.class);
    }

    public String getIndexName() {
        return "status-" + dateRangeKey;
    }
}
