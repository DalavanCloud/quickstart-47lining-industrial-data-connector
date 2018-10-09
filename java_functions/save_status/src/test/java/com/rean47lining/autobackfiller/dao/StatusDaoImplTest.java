package com.rean47lining.autobackfiller.dao;

import com.google.common.collect.ImmutableList;
import com.rean47lining.autobackfiller.dto.StatusDto;
import com.rean47lining.autobackfiller.model.Status;
import com.rean47lining.autobackfiller.model.StatusType;
import org.apache.http.HttpHost;
import org.elasticsearch.action.admin.indices.create.CreateIndexRequest;
import org.elasticsearch.action.admin.indices.delete.DeleteIndexRequest;
import org.elasticsearch.action.admin.indices.refresh.RefreshRequest;
import org.elasticsearch.action.index.IndexRequest;
import org.elasticsearch.action.search.SearchRequest;
import org.elasticsearch.action.search.SearchResponse;
import org.elasticsearch.client.RestClient;
import org.elasticsearch.client.RestHighLevelClient;
import org.elasticsearch.common.xcontent.XContentType;
import org.elasticsearch.index.query.QueryBuilders;
import org.elasticsearch.search.SearchHit;
import org.elasticsearch.search.SearchHits;
import org.elasticsearch.search.builder.SearchSourceBuilder;
import org.joda.time.DateTime;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.stream.Stream;

import static org.junit.Assert.assertEquals;

public class StatusDaoImplTest {
    private StatusDaoImpl statusDaoImpl;
    private RestHighLevelClient client;
    private String indexName = "status-2012-12-12";

    @Before
    public void beforeEach() throws IOException {
        String elasticsearchHostname = "localhost";
        int elasticsearchPort = 9200;

        client = new RestHighLevelClient(
                RestClient.builder(
                        new HttpHost(elasticsearchHostname, elasticsearchPort)
                )
        );
        CreateIndexRequest createIndexRequest = new CreateIndexRequest(indexName);
        createIndexRequest.mapping("doc", new HashMap());
        statusDaoImpl = new StatusDaoImpl(client);
        client.indices().create(createIndexRequest);
    }

    @After
    public void afterEach() throws IOException {
        client.indices().delete(new DeleteIndexRequest(indexName));
    }

    @Test
    public void batchSaveStatusSingle() throws IOException {
        DateTime dateTime = new DateTime(
                2012,
                12,
                12,
                0,
                11,
                22
        );
        Status status = new Status(StatusType.RUNNING, dateTime);
        Stream<Status> statusStream = Stream.of(status);
        statusDaoImpl.batchSaveStatus(statusStream);

        client.indices().refresh(new RefreshRequest(indexName));
        SearchSourceBuilder sourceBuilder = new SearchSourceBuilder().query(QueryBuilders.matchAllQuery());
        SearchRequest searchRequest = new SearchRequest(indexName);
        searchRequest.source(sourceBuilder);
        SearchResponse searchResponse = client.search(searchRequest);

        long hits = searchResponse.getHits().totalHits;

        assertEquals(1, hits);
    }

    @Test
    public void batchSaveStatusMultiple() throws IOException {
        DateTime dateTime = new DateTime(
                2012,
                12,
                12,
                0,
                11,
                22
        );
        Status status1 = new Status(StatusType.RUNNING, dateTime);
        Status status2 = new Status(StatusType.RUNNING, dateTime);
        Stream<Status> statusStream = Stream.of(status1, status2);
        statusDaoImpl.batchSaveStatus(statusStream);

        client.indices().refresh(new RefreshRequest(indexName));
        SearchSourceBuilder sourceBuilder = new SearchSourceBuilder().query(QueryBuilders.matchAllQuery());
        SearchRequest searchRequest = new SearchRequest(indexName);
        searchRequest.source(sourceBuilder);
        SearchResponse searchResponse = client.search(searchRequest);

        long hits = searchResponse.getHits().totalHits;

        assertEquals(2, hits);
    }

    @Test
    public void batchSaveStatusNone() throws IOException {
        Stream<Status> statusStream = Stream.of();
        statusDaoImpl.batchSaveStatus(statusStream);

        client.indices().refresh(new RefreshRequest(indexName));
        SearchSourceBuilder sourceBuilder = new SearchSourceBuilder().query(QueryBuilders.matchAllQuery());
        SearchRequest searchRequest = new SearchRequest(indexName);
        searchRequest.source(sourceBuilder);
        SearchResponse searchResponse = client.search(searchRequest);

        long hits = searchResponse.getHits().totalHits;

        assertEquals(0, hits);
    }

    @Test
    public void testGetStatusesFromTimeRangeOne() throws IOException {
        DateTime first = new DateTime(2012, 12, 12, 0, 30, 0);
        StatusDto statusDto1 = new StatusDto(new Status(StatusType.RUNNING, first));
        StatusDto statusDto2 = new StatusDto(new Status(StatusType.RUNNING, first.minusMinutes(15)));
        StatusDto statusDto3 = new StatusDto(new Status(StatusType.RUNNING, first.plusMinutes(15)));
        List<StatusDto> statusDtoList = ImmutableList.of(statusDto1, statusDto2, statusDto3);
        for (StatusDto statusDto : statusDtoList)
            client.index(new IndexRequest(statusDto.getIndexName(), "doc")
                .source(statusDto.toJson(), XContentType.JSON));
        client.indices().refresh(new RefreshRequest("status-2012-12-12"));

        DateTime from = new DateTime(first.minusMinutes(1));
        DateTime to = new DateTime(first.plusMinutes(1));

        final List<Status> resultOne = new ArrayList<>();
        for (List<Status> searchHits : statusDaoImpl.getStatusesFromTimeRange(from, to))
           resultOne.addAll(searchHits);

        assertEquals(1, resultOne.size());
    }


    @Test
    public void testGetStatusesFromTimeRangeMultiple() throws IOException {
        DateTime first = new DateTime(2012, 12, 12, 0, 30, 0);
        StatusDto statusDto1 = new StatusDto(new Status(StatusType.RUNNING, first));
        StatusDto statusDto2 = new StatusDto(new Status(StatusType.RUNNING, first.minusMinutes(15)));
        StatusDto statusDto3 = new StatusDto(new Status(StatusType.RUNNING, first.plusMinutes(15)));
        List<StatusDto> statusDtoList = ImmutableList.of(statusDto1, statusDto2, statusDto3);
        for (StatusDto statusDto : statusDtoList)
            client.index(new IndexRequest(statusDto.getIndexName(), "doc")
                .source(statusDto.toJson(), XContentType.JSON));
        client.indices().refresh(new RefreshRequest("status-2012-12-12"));

        DateTime from = new DateTime(first.minusMinutes(15));
        DateTime to = new DateTime(first.plusMinutes(1));

        final List<Status> resultOne = new ArrayList<>();
        for (List<Status> searchHits : statusDaoImpl.getStatusesFromTimeRange(from, to))
           resultOne.addAll(searchHits);

        assertEquals(2, resultOne.size());
    }


    @Test
    public void testGetStatusesFromTimeRangeNone() throws IOException {
        DateTime first = new DateTime(2012, 12, 12, 0, 30, 0);
        StatusDto statusDto1 = new StatusDto(new Status(StatusType.RUNNING, first));
        StatusDto statusDto2 = new StatusDto(new Status(StatusType.RUNNING, first.minusMinutes(15)));
        StatusDto statusDto3 = new StatusDto(new Status(StatusType.RUNNING, first.plusMinutes(15)));
        List<StatusDto> statusDtoList = ImmutableList.of(statusDto1, statusDto2, statusDto3);
        for (StatusDto statusDto : statusDtoList)
            client.index(new IndexRequest(statusDto.getIndexName(), "doc")
                .source(statusDto.toJson(), XContentType.JSON));
        client.indices().refresh(new RefreshRequest("status-2012-12-12"));

        DateTime from = new DateTime(first.minusMinutes(17));
        DateTime to = new DateTime(first.minusMinutes(16));

        final List<Status> resultOne = new ArrayList<>();
        for (List<Status> searchHits : statusDaoImpl.getStatusesFromTimeRange(from, to))
           resultOne.addAll(searchHits);

        assertEquals(0, resultOne.size());
    }
}