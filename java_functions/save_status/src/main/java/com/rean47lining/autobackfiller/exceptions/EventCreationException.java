package com.rean47lining.autobackfiller.exceptions;

public class EventCreationException extends AutoBackfillerException {
    EventCreationException(String msg, Throwable cause) {
        super(msg, cause);
    }

    public EventCreationException(String msg) {
        super(msg);
    }
}
