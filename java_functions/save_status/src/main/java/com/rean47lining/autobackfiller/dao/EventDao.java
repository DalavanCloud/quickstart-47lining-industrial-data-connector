package com.rean47lining.autobackfiller.dao;

import com.rean47lining.autobackfiller.model.Event;

import java.sql.SQLException;

public interface EventDao {
    int insertEvent(Event event) throws SQLException;
}