package com.rean47lining.autobackfiller.dao;

import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.rean47lining.autobackfiller.dto.StatusDto;
import com.rean47lining.autobackfiller.model.Status;
import com.rean47lining.autobackfiller.utils.ElasticsearchResultSet;
import org.apache.http.HttpHost;
import org.apache.http.impl.nio.client.HttpAsyncClientBuilder;
import org.elasticsearch.action.bulk.BulkRequest;
import org.elasticsearch.action.index.IndexRequest;
import org.elasticsearch.action.search.SearchRequest;
import org.elasticsearch.client.RestClient;
import org.elasticsearch.client.RestHighLevelClient;
import org.elasticsearch.common.xcontent.XContentType;
import org.elasticsearch.index.query.RangeQueryBuilder;
import org.elasticsearch.search.builder.SearchSourceBuilder;
import org.joda.time.DateTime;
import vc.inreach.aws.request.AWSSigner;
import vc.inreach.aws.request.AWSSigningRequestInterceptor;

import javax.net.ssl.SSLContext;
import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.stream.Stream;

public class StatusDaoImpl implements StatusDao {
    private static final int DEFAULT_BATCH_SIZE = 6 * 100;
    private RestHighLevelClient client;

    public StatusDaoImpl() {
        String elasticsearchHostname = System.getenv("ELASTICSEARCH_HOST");
        int elasticsearchPort = Integer.parseInt(System.getenv("ELASTICSEARCH_PORT"));
        String region = System.getenv("REGION");
        client = new RestHighLevelClient(
                RestClient.builder(
                        new HttpHost(elasticsearchHostname, elasticsearchPort, "https")
                ).setHttpClientConfigCallback(httpClientBuilder -> {
                    HttpAsyncClientBuilder httpAsyncClientBuilder = null;
                    try {
                        httpAsyncClientBuilder = httpClientBuilder.setSSLContext(SSLContext.getDefault());
                        final AWSSigner awsSigner = new AWSSigner(
                                new DefaultAWSCredentialsProviderChain(),
                                region,
                                "es",
                                () -> LocalDateTime.now(ZoneOffset.UTC));
                        httpAsyncClientBuilder.addInterceptorLast(new AWSSigningRequestInterceptor(awsSigner));
                    } catch (NoSuchAlgorithmException e) {
                        e.printStackTrace();
                    }
                    return httpAsyncClientBuilder;
                })
        );
    }

    public StatusDaoImpl(RestHighLevelClient client) {
        this.client = client;
    }

    @Override
    public void batchSaveStatus(Stream<Status> statusCollection) throws IOException {
        BulkRequest bulkRequest = new BulkRequest();
        Stream<IndexRequest> indexRequests = statusCollection
                .map(status -> {
                    StatusDto statusDto = new StatusDto(status);
                    String asJson = statusDto.toJson();
                    return new IndexRequest(statusDto.getIndexName(), "doc")
                            .source(asJson, XContentType.JSON);
                });
        indexRequests.forEach(bulkRequest::add);
        if(bulkRequest.requests().size() > 0)
            client.bulk(bulkRequest);
    }

    @Override
    public ElasticsearchResultSet getStatusesFromTimeRange(DateTime from, DateTime to) {
        if(from.isAfter(to))
            throw new IllegalArgumentException(
                    String.format("From is greater than to. From: %s, to: %s", from.toString(), to.toString())
            );

        String fromStr = from.toString("yyyy-MM-dd'T'HH:mm:ss");
        String toStr = to.toString("yyyy-MM-dd'T'HH:mm:ss");
        RangeQueryBuilder rangeQueryBuilder = new RangeQueryBuilder("datetime");
        rangeQueryBuilder.gte(fromStr).lte(toStr);

        SearchSourceBuilder searchSourceBuilder = new SearchSourceBuilder();
        searchSourceBuilder.query(rangeQueryBuilder).sort("datetime");
        searchSourceBuilder.size(DEFAULT_BATCH_SIZE);

        SearchRequest searchRequest = new SearchRequest();
        searchRequest.source(searchSourceBuilder);

        return new ElasticsearchResultSet(client, searchRequest);
    }
}