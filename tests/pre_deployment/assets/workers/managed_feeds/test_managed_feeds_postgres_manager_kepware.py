from freezegun import freeze_time

from model.kepware.models import (
    Event,
    EventStatus,
    Feed,
    FeedGroup,
    SubscribeEvent,
)


@freeze_time('2016-01-02 11:12:13')
def test_handle_subscribe_request_with_success_kepware(managed_feeds_postgres_manager_kepware,
                                                       postgres_session_kepware):
    composition_event_id = 'cd485049-2f6f-4355-8970-05abb5fda70c|0'
    payload = {'feeds': ['Feed0', 'Feed1'], 'is_success': True}

    feed_list = list(map(lambda name: Feed(name=name), ['Feed0', 'Feed1', 'Feed2', 'Feed3']))
    postgres_session_kepware.add_all([
        *feed_list,
        SubscribeEvent(
            id='cd485049-2f6f-4355-8970-05abb5fda70c',
            status=EventStatus.pending,
            number_of_feeds=2
        ),
        FeedGroup(
            id='0',
            event_id='cd485049-2f6f-4355-8970-05abb5fda70c',
            feeds=['Feed0', 'Feed1'],
            status=EventStatus.pending
        ),
        FeedGroup(
            id='1',
            event_id='cd485049-2f6f-4355-8970-05abb5fda70c',
            feeds=['Feed2', 'Feed3'],
            status=EventStatus.success
        )
    ])

    managed_feeds_postgres_manager_kepware.handle_subscribe_request(composition_event_id, payload)

    postgres_session_kepware.expire_all()

    event = postgres_session_kepware.query(Event).get('cd485049-2f6f-4355-8970-05abb5fda70c')
    assert event.status == EventStatus.success

    assert feed_list[0].subscription_status['default'] == 'subscribed'
    assert feed_list[1].subscription_status['default'] == 'subscribed'
    assert feed_list[2].subscription_status['default'] == 'unsubscribed'
    assert feed_list[3].subscription_status['default'] == 'unsubscribed'
