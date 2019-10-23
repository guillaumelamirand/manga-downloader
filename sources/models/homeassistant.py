import logging
import json
import requests

_LOGGER = logging.getLogger(__name__)

class HomeAssistant(object):
    _MQTT_SERVICE_API = '/api/services/mqtt/publish'

    def __init__(self, config):        
        self.base_url = config['homeassistant']['base_url']
        self.token = config['homeassistant']['token']
        self.mqtt_topic = config['homeassistant']['mqtt_topic']
    
    def notify(self, notifications):
        json_payload = {
            "topic": self.mqtt_topic,
            "retain" : "false", 
            "payload": json.dumps(notifications, default=lambda x: x.__dict__)
            }

        response = requests.post(self.base_url + HomeAssistant._MQTT_SERVICE_API, json=json_payload, headers={'Authorization': 'Bearer %s' % self.token})
        if (response.status_code != 200):
            _LOGGER.error("Unable to send notifications to home assistant, code: %s" % response.status_code)
            response.raise_for_status()
        

class Notification(object):
    def __init__(self, manga_serie, chapiter, success):
        self.manga_serie = manga_serie
        self.chapiter = chapiter
        self.success = success

    def __repr__(self):
        return "%s(manga=%r, chapiter=%r, status=%r)" % (self.__class__.__name__, self.manga, self.chapiter, self.status)

