import enum


class SubscriptionStatus(enum.Enum):
    subscribed = 'subscribed'
    pending = 'pending'
    unsubscribed = 'unsubscribed'
    unknown = 'unknown'


class EventStatus(enum.Enum):
    pending = 'pending'
    failure = 'failure'
    success = 'success'
