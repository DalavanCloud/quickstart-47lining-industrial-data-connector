package com.rean47lining.autobackfiller;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.events.SNSEvent;
import com.rean47lining.autobackfiller.dao.StatusDao;
import com.rean47lining.autobackfiller.dao.StatusDaoImpl;
import com.rean47lining.autobackfiller.exceptions.UnexpectedRecordsSizeException;
import com.rean47lining.autobackfiller.model.Status;

import java.io.IOException;
import java.util.List;
import java.util.stream.Stream;

public class StatusSaver {
    public String handler(SNSEvent snsEvent, Context context) throws UnexpectedRecordsSizeException, IOException {
        LambdaLogger logger = context.getLogger();
        List<SNSEvent.SNSRecord> records = snsEvent.getRecords();
        if (records.size() < 1)
            throw new UnexpectedRecordsSizeException(
                    String.format("Cannot read records successfully... %s", records.toString())
            );

        Stream<Status> statusesToSave = records.stream().map(Status::new);
        logger.log(String.format("Received statuses to save: %s", statusesToSave.toString()));

        logger.log("Saving statuses...");
        StatusDao statusDao = new StatusDaoImpl();
        statusDao.batchSaveStatus(statusesToSave);
        logger.log("Statuses successfully saved.");

        return "OK";
    }
}