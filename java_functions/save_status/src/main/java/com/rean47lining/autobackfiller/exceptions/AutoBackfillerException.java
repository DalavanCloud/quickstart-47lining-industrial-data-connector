package com.rean47lining.autobackfiller.exceptions;

class AutoBackfillerException extends RuntimeException {
    AutoBackfillerException(String msg, Throwable cause) {
        super(msg, cause);
    }

    AutoBackfillerException(String msg) {
        super(msg);
    }
}

