from sqlalchemy import Column, String, Integer, Boolean, ARRAY, Text, DateTime, inspect, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from model.enums import EventStatus, SubscriptionStatus
from model.utils import utcnow

DATA_SOURCES = ['default']

Base = declarative_base()
event_status_enum = ENUM(EventStatus, metadata=Base.metadata)


class SubscribeEventMixin:
    @declared_attr
    def data_source(cls):
        return cls.__table__.c.get('data_source', Column(Text))


class BaseModel(Base):
    __abstract__ = True

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class Feed(BaseModel):
    __tablename__ = 'feed'

    name = Column(Text, primary_key=True)
    update_timestamp = Column(DateTime, nullable=False, server_default=utcnow(), onupdate=utcnow())

    subscription_status = Column(
        JSONB,
        nullable=False,
        default=lambda: {
            source: SubscriptionStatus.unsubscribed.value
            for source in DATA_SOURCES
        }
    )


class Event(BaseModel):
    __tablename__ = 'event'

    id = Column(Text, primary_key=True)
    type = Column(String(20), nullable=False)
    start_timestamp = Column(DateTime, nullable=False, server_default=utcnow())
    update_timestamp = Column(DateTime, nullable=False, server_default=utcnow(), onupdate=utcnow())
    status = Column(event_status_enum, nullable=False, server_default=EventStatus.pending.value)
    username = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    __mapper_args__ = {'polymorphic_on': type}


class Asset(BaseModel):
    __tablename__ = 'asset'

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=True)
    parent_id = Column(Text, ForeignKey('asset.id'))
    is_leaf = Column(Boolean, nullable=False)
    children = relationship('Asset', cascade="all,delete")

    description = Column(Text, nullable=True)


class Attribute(BaseModel):
    __tablename__ = 'attribute'

    id = Column(Text, primary_key=True)
    asset_id = Column(Text, nullable=False)
    name = Column(Text, nullable=True)
    feed = Column(Text, nullable=True)

    description = Column(Text, nullable=True)
    type = Column(Text, nullable=True)
    uom = Column(Text, nullable=True)
    item_name = Column(Text, nullable=True)


class SyncFeedsEvent(Event):

    @declared_attr
    def s3_bucket(cls):
        return cls.__table__.c.get('s3_bucket', Column(String(64)))

    @declared_attr
    def s3_key(cls):
        return cls.__table__.c.get('s3_key', Column(String(256)))

    __mapper_args__ = {
        'polymorphic_identity': 'sync_feeds',
    }


class SyncAsEvent(Event):
    database = Column(Text)

    @declared_attr
    def s3_bucket(cls):
        return cls.__table__.c.get('s3_bucket', Column(String(64)))

    @declared_attr
    def s3_key(cls):
        return cls.__table__.c.get('s3_key', Column(Text))

    __mapper_args__ = {
        'polymorphic_identity': 'sync_as'
    }


class FeedNamedEvent(Event):
    __abstract__ = True

    @declared_attr
    def name(cls):
        return cls.__table__.c.get('name', Column(Text))

    @declared_attr
    def number_of_feeds(cls):
        return cls.__table__.c.get('number_of_feeds', Column(Integer))

    @declared_attr
    def feed_groups(cls):
        return cls.__table__.c.get('feed_groups', relationship('FeedGroup', cascade="all,delete"))


class FeedGroup(BaseModel):
    __tablename__ = 'feed_group'

    id = Column(Integer, primary_key=True, nullable=False)
    event_id = Column(Text, ForeignKey('event.id'), primary_key=True, nullable=False)

    feeds = Column(ARRAY(Text))
    status = Column(event_status_enum, nullable=False, server_default=EventStatus.pending.value)
    error_message = Column(Text, nullable=True)


class BackfillEvent(FeedNamedEvent):
    __mapper_args__ = {
        'polymorphic_identity': 'backfill',
    }


class InterpolateEvent(FeedNamedEvent):
    __mapper_args__ = {
        'polymorphic_identity': 'interpolate',
    }


class SubscribeEvent(SubscribeEventMixin, FeedNamedEvent):
    __mapper_args__ = {
        'polymorphic_identity': 'subscribe',
    }


class UnsubscribeEvent(SubscribeEventMixin, FeedNamedEvent):
    __mapper_args__ = {
        'polymorphic_identity': 'unsubscribe',
    }


class ResetEvent(Event):
    __mapper_args__ = {
        'polymorphic_identity': 'reset',
    }


class Settings(BaseModel):
    __tablename__ = 'settings'

    name = Column(Text, primary_key=True)
    value = Column(Text)
