package com.rean47lining.autobackfiller.exceptions;

public class FeedGroupCreationException extends AutoBackfillerException {
    FeedGroupCreationException(String msg, Throwable cause) {
        super(msg, cause);
    }

    public FeedGroupCreationException(String msg) {
        super(msg);
    }
}
