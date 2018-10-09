package com.rean47lining.autobackfiller.model;

public enum EventStatus {
    FAILURE("failure"), PENDING("pending"), SUCCESS("success");

    private final String text;

    EventStatus(final String text) {
        this.text = text;
    }

    @Override
    public String toString() {
        return text;
    }
}
