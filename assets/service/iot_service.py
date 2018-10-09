
class IoTService(object):

    def __init__(self, iot_client, managed_feeds_dao):
        self.iot_client = iot_client
        self.managed_feeds_dao = managed_feeds_dao

    def create_things(self, feeds):
        for feed in feeds:
            feed = self._remove_forbidden_characters(feed)
            self.iot_client.create_thing(
                thingName=feed
            )

    def _remove_forbidden_characters(self, feed):
        """
        Thing name should match regex: [a-zA-Z0-9:_-]+
        """
        return feed.replace('.', '_')
