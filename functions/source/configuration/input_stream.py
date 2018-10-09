"""
Columns in input stream

Columns name, value, timestamp are default and should not be specified here
"""


additional_columns_stream = [
    {
        'column_name': 'data_source',
        'athena_type': 'STRING',
        'kinesis_type': 'VARCHAR(64)',
        'Mapping': '$.DataSource'
    }
]

input_stream_record_columns_pi = [
    {
        'Name': 'name',
        'SqlType': 'VARCHAR(64)'
    },
    {
        'Name': 'data_source',
        'SqlType': 'VARCHAR(64)'
    },
    {
        'Name': 'feed_value',
        'SqlType': 'VARCHAR(128)'
    },
    {
        'Name': 'feed_timestamp',
        'SqlType': 'VARCHAR(64)'
    }
]


input_stream_record_columns_wonderware = [
    {
        'Name': 'name',
        'SqlType': 'VARCHAR(64)'
    },
    {
        'Name': 'data_source',
        'SqlType': 'VARCHAR(64)'
    },
    {
        'Name': 'feed_value',
        'SqlType': 'VARCHAR(128)'
    },
    {
        'Name': 'feed_timestamp',
        'SqlType': 'VARCHAR(64)'
    }
]

input_stream_record_columns_kepware = [
    {
        'Name': 'name',
        'SqlType': 'VARCHAR(64)'
    },
    {
        'Name': 'feed_value',
        'SqlType': 'VARCHAR(128)'
    },
    {
        'Name': 'feed_timestamp',
        'SqlType': 'VARCHAR(64)'
    }
]
