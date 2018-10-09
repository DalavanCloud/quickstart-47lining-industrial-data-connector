package com.rean47lining.autobackfiller.model;

import com.google.common.base.MoreObjects;
import com.google.common.base.Objects;
import com.google.gson.Gson;

public class SubscriptionStatus {
    private SubscriptionStatusEnum archive;
    private SubscriptionStatusEnum snapshot;

    public SubscriptionStatus(SubscriptionStatusEnum archive, SubscriptionStatusEnum snapshot) {
        this.archive = archive;
        this.snapshot = snapshot;
    }

    public static SubscriptionStatus fromJson(String subscription_status) {
        return new Gson().fromJson(subscription_status, SubscriptionStatus.class);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        SubscriptionStatus that = (SubscriptionStatus) o;
        return Objects.equal(archive, that.archive) &&
                Objects.equal(snapshot, that.snapshot);
    }

    public SubscriptionStatusEnum getArchive() {
        return archive;
    }

    public SubscriptionStatusEnum getSnapshot() {
        return snapshot;
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(archive, snapshot);
    }

    @Override
    public String toString() {
        return MoreObjects.toStringHelper(this)
                .add("archive", archive)
                .add("snapshot", snapshot)
                .toString();
    }
}