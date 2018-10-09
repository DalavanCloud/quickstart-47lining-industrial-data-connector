JOIN_COLUMN_NAME = "FeedName"

additional_assets_columns_with_join_column = [
    {
        'column_name': JOIN_COLUMN_NAME,
        'athena_type': 'STRING',
        'kinesis_type': 'VARCHAR(64)',
        'Mapping': '$.FeedName'
    }
]
