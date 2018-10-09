package com.rean47lining.autobackfiller.model;

import com.google.gson.annotations.SerializedName;

public enum SubscriptionStatusEnum {
    @SerializedName("subscribed")
    SUBSCRIBED("subscribed"),
    @SerializedName("unsubscribed")
    UNSUBSCRIBED("unsubscribed");

    private final String text;

    SubscriptionStatusEnum(final String text) {
        this.text = text;
    }

    @Override
    public String toString() {
        return text;
    }
}