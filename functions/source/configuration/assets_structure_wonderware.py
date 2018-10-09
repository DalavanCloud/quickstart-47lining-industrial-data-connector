JOIN_COLUMN_NAME = "FeedName"

additional_assets_columns_with_join_column = [  # TODO Extend with wonderware columns
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
