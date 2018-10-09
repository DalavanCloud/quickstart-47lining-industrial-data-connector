package com.rean47lining.autobackfiller.dao;

import com.rean47lining.autobackfiller.model.FeedGroup;

import java.sql.SQLException;

public interface FeedGroupDao {
    int insertFeedGroup(FeedGroup feedGroup) throws SQLException;
}