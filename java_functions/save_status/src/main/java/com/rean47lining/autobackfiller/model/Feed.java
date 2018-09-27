package com.rean47lining.autobackfiller.model;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import org.joda.time.DateTime;

public class Feed {
    private String name;
    private DateTime updateTimestamp;
    private SubscriptionStatus subscriptionStatus;

    public Feed(String name, DateTime updateTimestamp, SubscriptionStatus subscriptionStatus) {
        this.name = name;
        this.updateTimestamp = updateTimestamp;
        this.subscriptionStatus = subscriptionStatus;
    }

    public String getName() {
        return name;
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("name", name)
                .add("updateTimestamp", updateTimestamp)
                .add("subscriptionStatus", subscriptionStatus)
                .toString();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Feed feed = (Feed) o;
        return Objects.equal(name, feed.name) &&
                Objects.equal(updateTimestamp, feed.updateTimestamp) &&
                Objects.equal(subscriptionStatus, feed.subscriptionStatus);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(name, updateTimestamp, subscriptionStatus);
    }
}
