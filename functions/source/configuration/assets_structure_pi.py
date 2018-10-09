JOIN_COLUMN_NAME = "FeedName"

additional_assets_columns_with_join_column = [
    {
        'column_name': 'AsPath',
        'athena_type': 'STRING',
        'kinesis_type': 'VARCHAR(64)',
        'Mapping': '$.AsPath'
    },
    {
        'column_name': 'Asset',
        'athena_type': 'STRING',
        'kinesis_type': 'VARCHAR(64)',
        'Mapping': '$.Asset'
    },
    {
        'column_name': 'Categories',
        'athena_type': 'STRING',
        'kinesis_type': 'VARCHAR(128)',
        'Mapping': '$.Categories[0:]'
    },
    {
        'column_name': 'Description',
        'athena_type': 'STRING',
        'kinesis_type': 'VARCHAR(128)',
        'Mapping': '$.Description'
    },
    {
        'column_name': 'AttributeName',
        'athena_type': 'STRING',
        'kinesis_type': 'VARCHAR(64)',
        'Mapping': '$.Name'
    },
    {
        'column_name': 'FeedPath',
        'athena_type': 'STRING',
        'kinesis_type': 'VARCHAR(64)',
        'Mapping': '$.FeedPath'
    },
    {
        'column_name': 'Template',
        'athena_type': 'STRING',
        'kinesis_type': 'VARCHAR(64)',
        'Mapping': '$.Template'
    },
    {
        'column_name': 'UOM',
        'athena_type': 'STRING',
        'kinesis_type': 'VARCHAR(64)',
        'Mapping': '$.UOM'
    },
    {
        'column_name': JOIN_COLUMN_NAME,
        'athena_type': 'STRING',
        'kinesis_type': 'VARCHAR(64)',
        'Mapping': '$.FeedName'
    }
]
