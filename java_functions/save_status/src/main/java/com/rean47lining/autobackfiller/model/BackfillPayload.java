package com.rean47lining.autobackfiller.model;

import org.joda.time.DateTime;

import java.util.List;

public class BackfillPayload {
    private boolean use_query_syntax;
    private String backfill_name;
    private DateTime from;
    private DateTime to;
    private List<String> feeds;

    public BackfillPayload(boolean use_query_syntax, String backfill_name, DateTime from, DateTime to, List<String> feeds) {
        this.use_query_syntax = use_query_syntax;
        this.backfill_name = backfill_name;
        this.from = from;
        this.to = to;
        this.feeds = feeds;
    }
}