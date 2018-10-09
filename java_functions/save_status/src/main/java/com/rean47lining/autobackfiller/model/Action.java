package com.rean47lining.autobackfiller.model;

import com.google.gson.annotations.SerializedName;

public enum Action {
    @SerializedName("backfill")
    BACKFILL("backfill");

    private final String text;

    Action(final String text) {
        this.text = text;
    }

    @Override
    public String toString() {
        return text;
    }
}
