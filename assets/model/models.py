import enum

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Boolean, ARRAY, Text, DateTime, Enum, inspect, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship

Base = declarative_base()


class utcnow(expression.FunctionElement):
    type = DateTime()


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class SubscriptionStatus(enum.Enum):
    subscribed = 'subscribed'
    pending = 'pending'
    unsubscribed = 'unsubscribed'


class EventStatus(enum.Enum):
    pending = 'pending'
    failure = 'failure'
    success = 'success'


class BaseModel(Base):
    __abstract__ = True

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class PiPoint(BaseModel):
    __tablename__ = 'pipoint'

    pi_point = Column(Text, primary_key=True)
    subscription_status = Column(
        Enum(SubscriptionStatus),
        nullable=False,
        server_default=SubscriptionStatus.unsubscribed.value
    )
    update_timestamp = Column(DateTime, nullable=False, server_default=utcnow(), onupdate=utcnow())


class Event(BaseModel):
    __tablename__ = 'event'

    id = Column(Text, primary_key=True)
    event_type = Column(String(20), nullable=False)
    error_message = Column(Text, nullable=True)
    status = Column(Enum(EventStatus), nullable=False, server_default=EventStatus.pending.value)
    update_timestamp = Column(DateTime, nullable=False, server_default=utcnow(), onupdate=utcnow())

    __mapper_args__ = {'polymorphic_on': event_type}


class Asset(BaseModel):
    __tablename__ = 'asset'

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    template = Column(Text, nullable=True)
    parent_id = Column(Text, ForeignKey('asset.id'))
    is_leaf = Column(Boolean, nullable=False)
    categories = Column(ARRAY(Text), nullable=True)

    children = relationship('Asset', cascade="all,delete")


class Attribute(BaseModel):
    __tablename__ = 'attribute'

    id = Column(Text, primary_key=True)
    asset_id = Column(Text, nullable=True)
    name = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    type = Column(Text, nullable=True)
    categories = Column(ARRAY(Text), nullable=True)

    pi_point = Column(Text, nullable=True)


class SyncPiPointsEvent(Event):

    @declared_attr
    def s3_bucket(cls):
        return Event.__table__.c.get('s3_bucket', Column(String(64)))

    @declared_attr
    def s3_key(cls):
        return Event.__table__.c.get('s3_key', Column(String(256)))

    __mapper_args__ = {
        'polymorphic_identity': 'sync_pi_points',
    }


class SyncAfEvent(Event):
    database = Column(Text)

    @declared_attr
    def s3_bucket(cls):
        return Event.__table__.c.get('s3_bucket', Column(String(64)))

    @declared_attr
    def s3_key(cls):
        return Event.__table__.c.get('s3_key', Column(Text))

    __mapper_args__ = {
        'polymorphic_identity': 'sync_af'
    }


class PiPointEvent(Event):
    __abstract__ = True

    @declared_attr
    def pi_points(cls):
        return Event.__table__.c.get('pi_points', Column(ARRAY(Text)))


class PiPointNamedEvent(PiPointEvent):
    __abstract__ = True

    @declared_attr
    def name(cls):
        return Event.__table__.c.get('name', Column(Text))


class BackfillEvent(PiPointNamedEvent):

    __mapper_args__ = {
        'polymorphic_identity': 'backfill',
    }


class InterpolateEvent(PiPointNamedEvent):

    __mapper_args__ = {
        'polymorphic_identity': 'interpolate',
    }


class SubscribeEvent(PiPointEvent):

    __mapper_args__ = {
        'polymorphic_identity': 'subscribe',
    }


class UnsubscribeEvent(PiPointEvent):

    __mapper_args__ = {
        'polymorphic_identity': 'unsubscribe',
    }


class Settings(BaseModel):
    __tablename__ = 'settings'

    name = Column(Text, primary_key=True)
    value = Column(Text)
