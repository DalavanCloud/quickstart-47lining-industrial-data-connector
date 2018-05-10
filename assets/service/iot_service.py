
class IoTService(object):

    def __init__(self, iot_client, managed_feeds_dao):
        self.iot_client = iot_client
        self.managed_feeds_dao = managed_feeds_dao

    def create_things(self, pi_points):
        for pi_point in pi_points:
            pi_point = self._remove_forbidden_characters(pi_point)
            self.iot_client.create_thing(
                thingName=pi_point
            )

    def _remove_forbidden_characters(self, pi_point):
        """
        Thing name should match regex: [a-zA-Z0-9:_-]+
        """
        return pi_point.replace('.', '_')