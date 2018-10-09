package com.rean47lining.autobackfiller.dto;

import com.rean47lining.autobackfiller.model.Status;
import com.rean47lining.autobackfiller.model.StatusType;
import org.joda.time.DateTime;
import org.joda.time.Instant;
import org.junit.Test;

import java.text.ParseException;

import static org.junit.Assert.*;

public class StatusDtoTest {

    @Test
    public void toJson() throws ParseException {
        StatusDto statusDto = new StatusDto();
        statusDto.setDateRangeKey("2012-01-01");
        statusDto.setDatetime(Instant.parse("2012-01-01T00:11:22").toDate());
        statusDto.setStatus("RUNNING");

        String result = statusDto.toJson();

        assertEquals("{\"dateRangeKey\":\"2012-01-01\",\"datetime\":\"2012-01-01T00:11:22\"," +
                "\"status\":\"RUNNING\"}", result);
    }

    @Test
    public void fromJson() throws ParseException {
        String json = "{\"dateRangeKey\":\"2012-01-01\",\"datetime\":\"2012-01-01T00:11:22\",\"status\":\"RUNNING\"}";

        StatusDto result = StatusDto.fromJson(json);

        assertEquals("2012-01-01", result.getDateRangeKey());
        assertEquals(
                Instant.parse("2012-01-01T00:11:22").toDate(),
                result.getDatetime()
        );
        assertEquals("RUNNING", result.getStatus());
    }

    @Test
    public void statusToStatusDto() throws ParseException {
        Status status = new Status(
                StatusType.RUNNING,
                new DateTime(
                        2012,
                        1,
                        2,
                        0,
                        11,
                        22
                )
        );

        StatusDto result = new StatusDto(status);

        assertEquals("RUNNING", result.getStatus());
        assertEquals("2012-01-02", result.getDateRangeKey());
        assertEquals(
                Instant.parse("2012-01-02T00:11:22").toDate(),
                result.getDatetime()
        );
    }
}