package com.rean47lining.autobackfiller.model;

import com.google.gson.*;
import org.joda.time.DateTime;
import org.joda.time.format.ISODateTimeFormat;
import java.util.List;
import java.util.UUID;

public class BackfillRequest {
    private String id;
    private Action action = Action.BACKFILL;
    private BackfillPayload payload;

    public BackfillRequest(String id, BackfillPayload payload) {
        this.id = id;
        this.payload = payload;
    }

    public static BackfillRequest createBackfillRequest(DateTime lhsTimestamp, DateTime rhsTimestamp, UUID uuid,
                                                        List<String> feeds) {
        BackfillPayload backfillPayload = new BackfillPayload(
                false,
                "Backfill",
                lhsTimestamp,
                rhsTimestamp,
                feeds
        );
        return new BackfillRequest(
                uuid.toString(),
                backfillPayload
        );
    }

    private Gson gson() {
        return new GsonBuilder()
                .registerTypeAdapter(DateTime.class,
                        (JsonSerializer<DateTime>) (json, typeOfSrc, context) ->
                                new JsonPrimitive(ISODateTimeFormat.dateTime().print(json)))
                .registerTypeAdapter(DateTime.class,
                        (JsonDeserializer<DateTime>) (json, typeOfT, context) ->
                                ISODateTimeFormat.dateTime().parseDateTime(json.getAsString()))
                .create();
    }

    public String toChunkJson(int chunk) {
        id = id + "|" + String.valueOf(chunk);
        return gson().toJson(this);
    }
}