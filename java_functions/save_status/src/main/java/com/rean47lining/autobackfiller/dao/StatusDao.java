package com.rean47lining.autobackfiller.dao;

import com.rean47lining.autobackfiller.model.Status;
import com.rean47lining.autobackfiller.utils.ElasticsearchResultSet;
import org.joda.time.DateTime;

import java.io.IOException;
import java.util.stream.Stream;

public interface StatusDao {
    void batchSaveStatus(Stream<Status> statusCollection) throws IOException;

    ElasticsearchResultSet getStatusesFromTimeRange(DateTime from, DateTime to);
}

