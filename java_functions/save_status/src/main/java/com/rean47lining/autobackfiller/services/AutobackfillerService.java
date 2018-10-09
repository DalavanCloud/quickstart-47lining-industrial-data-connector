package com.rean47lining.autobackfiller.services;

import com.rean47lining.autobackfiller.model.Status;
import org.joda.time.DateTime;

import java.sql.SQLException;
import java.util.List;

public interface AutobackfillerService {
    void backfill(List<Status> statusList, DateTime beginWindow, DateTime endWindot) throws SQLException;
}
