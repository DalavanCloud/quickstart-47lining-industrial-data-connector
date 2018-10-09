package com.rean47lining.autobackfiller.utils;

import com.rean47lining.autobackfiller.exceptions.ElasticSearchScrollException;
import com.rean47lining.autobackfiller.model.Status;
import org.elasticsearch.action.search.ClearScrollRequest;
import org.elasticsearch.action.search.SearchRequest;
import org.elasticsearch.action.search.SearchResponse;
import org.elasticsearch.action.search.SearchScrollRequest;
import org.elasticsearch.client.RequestOptions;
import org.elasticsearch.client.RestHighLevelClient;
import org.elasticsearch.common.unit.TimeValue;
import org.elasticsearch.search.Scroll;
import org.elasticsearch.search.SearchHits;

import java.io.IOException;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;

public class ElasticsearchResultSet implements Iterable<List<Status>>, AutoCloseable {
    private final RestHighLevelClient client;
    private SearchRequest searchRequest;
    private long pageSize;
    private String scrollId = "";
    private long latestBatchSize = 0;
    private Scroll scroll = new Scroll(TimeValue.timeValueMinutes(1L));

    public ElasticsearchResultSet(RestHighLevelClient client, SearchRequest searchRequest) {
        this.client = client;
        this.searchRequest = searchRequest;
        this.pageSize = 0;
        this.pageSize = searchRequest.source().size();
    }

    @Override
    public Iterator<List<Status>> iterator() {
        return new Iterator<List<Status>>() {
            boolean isFirstBatch = true;

            @Override
            public boolean hasNext() {
                return isFirstBatch || latestBatchSize == pageSize;
            }

            @Override
            public List<Status> next() {
                SearchResponse searchResponse;
                try {
                    if (isFirstBatch) {
                        searchRequest.scroll(scroll);
                        searchResponse = client.search(searchRequest, RequestOptions.DEFAULT);
                        isFirstBatch = false;
                    } else {
                        SearchScrollRequest scrollRequest = new SearchScrollRequest(scrollId);
                        scrollRequest.scroll(scroll);
                        searchResponse = client.scroll(scrollRequest, RequestOptions.DEFAULT);
                    }
                    scrollId = searchResponse.getScrollId();
                } catch (IOException e) {
                    throw new ElasticSearchScrollException(
                            String.format("Cannot properly retrieve results, scroll id: %s", scrollId), e);
                }

                SearchHits hits = searchResponse.getHits();
                if (hits == null || hits.getHits() == null)
                    throw new NoSuchElementException();

                latestBatchSize = hits.getHits().length;

                return Status.fromSearchHits(hits);
            }
        };
    }

    @Override
    public void close() throws IOException {
        ClearScrollRequest clearScrollRequest = new ClearScrollRequest();
        clearScrollRequest.addScrollId(scrollId);
        client.clearScroll(clearScrollRequest, RequestOptions.DEFAULT);
        client.close();
    }
}
