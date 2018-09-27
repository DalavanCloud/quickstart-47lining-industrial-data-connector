package com.rean47lining.autobackfiller;

import com.rean47lining.autobackfiller.utils.ConnectionService;
import org.apache.commons.dbutils.QueryRunner;
import org.apache.commons.dbutils.ResultSetHandler;
import org.apache.commons.dbutils.handlers.MapListHandler;

import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.Map;

public class RDBSUtils {
    private final ConnectionService connectionService;

    public RDBSUtils(ConnectionService connectionService) {
        this.connectionService = connectionService;
    }

    private void executeStatement(String sql) throws SQLException {
        try(Connection connection = connectionService.getConnection()) {
            Statement statement = connection.createStatement();
            statement.executeUpdate(sql);
        }
    }

    public void createEventTable() throws SQLException {
        String sqlTable = "CREATE TABLE public.event (\n" +
                "    id text NOT NULL,\n" +
                "    type character varying(20) NOT NULL,\n" +
                "    start_timestamp timestamp without time zone DEFAULT timezone('utc'::text, now()) NOT NULL,\n" +
                "    update_timestamp timestamp without time zone DEFAULT timezone('utc'::text, now()) NOT NULL,\n" +
                "    status public.eventstatus DEFAULT 'pending'::public.eventstatus NOT NULL,\n" +
                "    error_message text,\n" +
                "    s3_bucket character varying(64),\n" +
                "    s3_key character varying(256),\n" +
                "    database text,\n" +
                "    name text,\n" +
                "    number_of_feeds integer,\n" +
                "    data_source text\n" +
                ");\n" +
                "\n" +
                "ALTER TABLE ONLY public.event ADD CONSTRAINT event_pkey PRIMARY KEY (id);\n";
        executeStatement("CREATE TYPE public.eventstatus AS ENUM ('success', 'failure', 'pending');");
        executeStatement(sqlTable);
    }

    public void deleteEventTable() throws SQLException {
        String deleteEventTable = "DROP TABLE public.event CASCADE";
        String deleteOtherRelations = "DROP TYPE public.eventstatus CASCADE";
        executeStatement(deleteEventTable);
        executeStatement(deleteOtherRelations);
    }

    public void createFeedsTable() throws SQLException {
        String sqlTable = "CREATE TABLE public.feed (\n" +
                "    name text NOT NULL,\n" +
                "    update_timestamp timestamp without time zone DEFAULT timezone('utc'::text, now()) NOT NULL,\n" +
                "    subscription_status jsonb NOT NULL\n" +
                ");\n";
        executeStatement(sqlTable);
    }

    public void deleteFeedsTable() throws SQLException {
        executeStatement("DROP TABLE public.feed");
    }

    public void insert(String insertSql, Object... params) throws SQLException {
        executeInsert(insertSql, params);
    }

    private void executeInsert(String insertSql, Object... params) throws SQLException {
        try(Connection connection = connectionService.getConnection()) {
            QueryRunner queryRunner = new QueryRunner();
            queryRunner.update(connection, insertSql, params);
        }
    }

    public List<Map<String, Object>> query(String sql) throws SQLException {
        try(Connection connection = connectionService.getConnection()) {
            QueryRunner queryRunner = new QueryRunner();
            return queryRunner.query(connection, sql, new MapListHandler());
        }
    }

    public void truncateFeedsTable() throws SQLException {
        executeStatement("TRUNCATE public.feed");
    }

    public void createFeedGroupTable() throws SQLException {
        executeStatement("CREATE TABLE public.feed_group (\n" +
                "    id integer NOT NULL,\n" +
                "    event_id text NOT NULL,\n" +
                "    feeds text[],\n" +
                "    status public.eventstatus DEFAULT 'pending'::public.eventstatus NOT NULL,\n" +
                "    error_message text\n" +
                ");\n" +
                "ALTER TABLE ONLY public.feed_group\n" +
                "    ADD CONSTRAINT feed_group_pkey PRIMARY KEY (id, event_id);\n" +
                "ALTER TABLE ONLY public.feed_group\n" +
                "    ADD CONSTRAINT feed_group_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.event(id);\n");
    }

    public void deleteFeedGroupTable() throws SQLException {
        executeStatement("DROP TABLE public.feed_group CASCADE");
    }

    public void truncateFeedGroupTable() throws SQLException {
        executeStatement("TRUNCATE public.feed_group CASCADE");
    }

    public void truncateEventTable() throws SQLException {
        executeStatement("TRUNCATE public.event CASCADE");
    }
}
