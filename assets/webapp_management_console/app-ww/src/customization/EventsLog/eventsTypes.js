export const eventsTypesMapping =  {
    sync_feeds: 'sync feeds',
    sync_as: 'sync structure',
    backfill: 'backfill',
    subscribe: 'subscribe',
    unsubscribe: 'unsubscribe',
    reset: 'reset data'
}

export const defaultEventAttributes = [
    'update_timestamp',
    'type',
    'status'
]

export const eventAttributesMapping = {
    'start_timestamp': 'start time',
    'feeds': 'feeds'
}
