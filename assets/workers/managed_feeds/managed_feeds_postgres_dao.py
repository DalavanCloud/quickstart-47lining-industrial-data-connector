from model.models import (
    SyncAfEvent,
    EventStatus,
    PiPoint,
    Event,
    SyncPiPointsEvent,
    BackfillEvent,
    InterpolateEvent,
    SubscribeEvent,
    UnsubscribeEvent,
    SubscriptionStatus,
    Asset,
    Attribute,
    Settings
)


class ManagedFeedsPostgresDao:

    def __init__(self, session, s3_client, cache_dir='/tmp/af_structure_cache'):
        self.session = session
        self.s3_client = s3_client
        self.cache_dir = cache_dir

    def recent_events(self, limit):
        events = self.session.query(Event).order_by(Event.update_timestamp.desc()).limit(limit)
        return [event.as_dict() for event in events]

    def get_pi_points(self, limit):
        pi_points = self.session.query(PiPoint).filter(PiPoint.subscription_status == SubscriptionStatus.unsubscribed).limit(limit)
        return [pi_point.as_dict() for pi_point in pi_points]

    def get_event_by_id(self, event_id):
        event = self.session.query(Event).get(event_id)
        if event is not None:
            return event.as_dict()

    @staticmethod
    def _paginate_query(query, page=None, page_size=None):
        if page_size:
            query = query.limit(page_size)
        if page:
            query = query.offset(page * page_size)
        return query

    def get_settings(self):
        settings = self.session.query(Settings).all()
        return {setting.name: setting.value for setting in settings}

    def save_settings(self, settings):
        for name, value in settings.items():
            self.session.merge(Settings(name=name, value=value))
        self.session.commit()

    def list_pi_points(self, page=None, page_size=None):
        query = self.session.query(PiPoint).order_by(PiPoint.pi_point)
        query = self._paginate_query(query, page=page, page_size=page_size)
        points = query.all()
        total_count = self.session.query(PiPoint).count()
        return {
            'pi_points': [point.as_dict() for point in points],
            'total_count': total_count
        }

    def search_pi_points(self, filters=None, pattern=None, pi_points=None, status=None, use_regex=False, page=None, page_size=None):
        if filters is not None:
            query = self.session.query(Attribute.pi_point)
            query = self._filter_query(query, filters)
            query = query.filter(Attribute.asset_id == Asset.id)\
                .filter(Attribute.pi_point.isnot(None))\
                .distinct(Attribute.pi_point).subquery()
            query = self.session.query(PiPoint).filter(PiPoint.pi_point.in_(query))
        else:
            query = self.session.query(PiPoint).order_by(PiPoint.pi_point)
            if pattern is not None and pattern != '':
                if use_regex:
                    query = query.filter(PiPoint.pi_point.op('~')(pattern))
                else:
                    query = query.filter(PiPoint.pi_point.ilike(pattern.replace('*', '%')))
            if pi_points is not None:
                query = query.filter(PiPoint.pi_point.in_(pi_points))
            if status is not None:
                query = query.filter(PiPoint.subscription_status == SubscriptionStatus[status])

        paginated_query = self._paginate_query(query, page=page, page_size=page_size)
        points = paginated_query.all()
        total_count = query.count()
        return {
            'pi_points': [point.as_dict() for point in points],
            'total_count': total_count
        }

    def _replace_wildcard(self, query):
        return query.replace('.*', '%').replace('*', '%')

    def _filter_query(self, query, filters):

        filter_actions = {
            'asset': {
                'name': lambda query: query.filter(Asset.name.like(self._replace_wildcard(filter['value']))),
                'description': lambda query: query.filter(Asset.description.like(self._replace_wildcard(filter['value']))),
                'template': lambda query: query.filter(Asset.template.like(self._replace_wildcard(filter['value']))),
                'path': lambda query: query.filter(Asset.id.like(self._replace_wildcard(filter['value'].replace('\\', '\\\\')))),
                'category': lambda query: query.filter(Asset.categories.any(filter['value']))
            },
            'attribute': {
                'name': lambda query: query.filter(Attribute.name.like(self._replace_wildcard(filter['value']))),
                'description': lambda query: query.filter(Attribute.description.like(self._replace_wildcard(filter['value']))),
                'category': lambda query: query.filter(Attribute.categories.any(filter['value'])),
                'point': lambda query: query.filter(Attribute.pi_point.like(self._replace_wildcard(filter['value'])))
            }
        }

        for filter in filters:
            filter['value'] = filter['value'].strip()
            if filter['type'] == 'attribute':
                query = query.filter(Attribute.asset_id == Asset.id)
            try:
                query = filter_actions[filter['type']][filter['parameter']](query)
            except KeyError:
                print('dsgff')

        return query

    def search_assets(self, filters, page=None, page_size=None):
        query = self.session.query(Asset)
        query = self._filter_query(query, filters)

        pi_points_total_count = query.filter(Attribute.asset_id == Asset.id)\
            .filter(Attribute.pi_point.isnot(None))\
            .distinct(Attribute.pi_point).count()

        query = query.group_by(Asset.id)
        query = query.order_by(Asset.id)
        paginated_query = self._paginate_query(query, page=page, page_size=page_size)
        assets = paginated_query.all()
        total_count = query.count()
        return {
            'assets': [asset.as_dict() for asset in assets],
            'total_count': total_count,
            'pi_points_total_count': pi_points_total_count
        }

    def search_asset_attributes(self, asset_id, filters):
        query = self.session.query(Attribute, PiPoint.subscription_status).\
            outerjoin(PiPoint, Attribute.pi_point == PiPoint.pi_point).\
            filter(Attribute.asset_id == asset_id)

        query = self._filter_query(query, filters)

        pi_points_total_count = query.filter(Attribute.pi_point.isnot(None)).distinct(Attribute.pi_point).count()

        attributes = query.all()
        total_count = query.count()

        return {
            'attributes': [
                {**attribute[0].as_dict(), 'subscription_status': attribute[1]}
                for attribute in attributes
            ],
            'total_count': total_count,
            'pi_points_total_count': pi_points_total_count
        }

    def get_asset_children(self, parent_asset_id):
        assets = self.session.query(Asset.id, Asset.name, Asset.is_leaf).\
            filter(Asset.parent_id == parent_asset_id).all()

        assets = [{'id': asset[0], 'name': asset[1], 'isLeaf': asset[2]} for asset in assets]
        return assets

    def update_pi_points(self, pi_points):
        all_pi_points = set(point[0] for point in self.session.query(PiPoint.pi_point).all())
        pi_points = set(pi_points)
        pi_points_to_remove = all_pi_points - pi_points
        pi_points_to_add = pi_points - all_pi_points

        self.session.query(PiPoint) \
            .filter(PiPoint.pi_point.in_(pi_points_to_remove)) \
            .delete(synchronize_session=False)

        self.session.bulk_insert_mappings(
            PiPoint,
            [{'pi_point': pi_point} for pi_point in pi_points_to_add]
        )
        self.session.commit()

    def _save_af_to_db(self, nodes, root_path):
        if nodes is None:
            return None
        else:
            for node in nodes:
                asset = {
                    'id': node['path'],
                    'name': node['name'],
                    'description': node.get('description'),
                    'template': node.get('template'),
                    'parent_id': root_path,
                    'is_leaf': len(node.get('assets', [])) == 0,
                    'categories': node.get('categories')
                }
                self.session.add(Asset(**asset))
                for attribute in node['attributes'] or []:
                    pi_point = attribute['point']['name'] if attribute['point'] is not None else None
                    attribute = {
                        'id': "{}|{}".format(node['path'], attribute.get('name')),
                        'asset_id': node['path'],
                        'name': attribute.get('name'),
                        'type': attribute.get('type'),
                        'pi_point': pi_point,
                        'description': attribute.get('description'),
                        'categories': None if attribute.get('categories') is None
                        else [category['name'] for category in attribute['categories']]
                    }
                    self.session.add(Attribute(**attribute))

                self._save_af_to_db(
                    node.get('assets'), node['path']
                )
        return None

    def update_af_structure(self, af_structure):
        self.session.query(Attribute).delete()
        self.session.query(Asset).delete()

        self._save_af_to_db([af_structure], None)

        self.session.commit()

    def update_pi_points_status(self, pi_points, status):
        self.session.query(PiPoint)\
            .filter(PiPoint.pi_point.in_(pi_points))\
            .update({'subscription_status': status}, synchronize_session=False)
        self.session.commit()

    def update_event_status(self, id, error_message=None):
        status = EventStatus.success if error_message is None else EventStatus.failure
        self.session.query(Event)\
            .filter(Event.id == id)\
            .update({'status': status, 'error_message': error_message}, synchronize_session=False)
        self.session.commit()

    def create_sync_pi_points_event(self, id, s3_bucket, s3_key):
        self.session.add(SyncPiPointsEvent(id=id, s3_bucket=s3_bucket, s3_key=s3_key))
        self.session.commit()

    def create_assets_sync_event(self, id, database, s3_bucket, s3_key):
        self.session.add(SyncAfEvent(id=id, s3_bucket=s3_bucket, s3_key=s3_key, database=database))
        self.session.commit()

    def create_event(self, id, pi_points, event_type):
        event_type_to_cls = {
            'subscribe': SubscribeEvent,
            'unsubscribe': UnsubscribeEvent
        }
        assert event_type in event_type_to_cls
        cls = event_type_to_cls[event_type]
        self.session.add(cls(id=id, pi_points=pi_points))
        self.session.commit()

    def create_backfill_event(self, id, pi_points, name):
        self.session.add(BackfillEvent(id=id, pi_points=pi_points, name=name))
        self.session.commit()

    def create_interpolation_event(self, id, pi_points, name):
        self.session.add(InterpolateEvent(id=id, pi_points=pi_points, name=name))
        self.session.commit()

    def clean_session(self):
        self.session.remove()
