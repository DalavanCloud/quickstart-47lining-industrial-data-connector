package com.rean47lining.autobackfiller.dao;

import com.rean47lining.autobackfiller.model.Feed;
import com.rean47lining.autobackfiller.model.SubscriptionStatus;

import java.sql.SQLException;
import java.util.List;

public interface FeedsDao {
    List<Feed> getFeeds(SubscriptionStatus subscriptionStatus, String operator) throws SQLException;

    List<Feed> getSubscribedFeeds() throws SQLException;
}