package com.rean47lining.autobackfiller.model;

import com.amazonaws.services.lambda.runtime.events.SNSEvent;
import com.rean47lining.autobackfiller.dto.StatusDto;
import org.elasticsearch.search.SearchHit;
import org.elasticsearch.search.SearchHits;
import org.joda.time.DateTime;

import java.util.ArrayList;
import java.util.List;

public class Status {
    private StatusType statusType;
    private DateTime timestamp;

    public Status(StatusType statusType, DateTime timestamp) {
        this.statusType = statusType;
        this.timestamp = timestamp;
    }

    public Status(SNSEvent.SNSRecord record) {
        String rawStatus = record.getSNS().getMessage();
        statusType = StatusType.valueOf(rawStatus);
        timestamp = record.getSNS().getTimestamp();
    }

    public Status(StatusDto statusDto) {
        timestamp = new DateTime(statusDto.getDatetime());
        statusType = StatusType.valueOf(statusDto.getStatus());
    }

    public static List<Status> fromSearchHits(SearchHits searchHits) {
        List<Status> result = new ArrayList<>();
        for (SearchHit hit : searchHits.getHits())
            result.add(Status.fromSearchHit(hit));
        return result;
    }

    private static Status fromSearchHit(SearchHit hit) {
        StatusDto statusDto = StatusDto.fromJson(hit.getSourceAsString());
        return new Status(statusDto);
    }

    public StatusType getStatusType() {
        return statusType;
    }

    public DateTime getTimestamp() {
        return timestamp;
    }

    @Override
    public String toString() {
        return com.google.common.base.MoreObjects.toStringHelper(this)
                .add("statusType", statusType)
                .add("timestamp", timestamp)
                .toString();
    }
}