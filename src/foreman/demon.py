import datetime
import pika
from pymongo import MongoClient
from bson import json_util
import json

__author__ = 'sam'


class PersistenceManager(object):

    minutes = 15

    def __init__(self,mongodb_host='localhost', mongodb_port=27017, mongodb_name='foreman'):
        self.client = MongoClient(mongodb_host, mongodb_port)
        self.db = self.client[mongodb_name]


    def find_storage_to_update(self):
        d = datetime.datetime.now() - datetime.timedelta(minutes=self.minutes)
        return self.db['storages'].find({"last-updated": {"$lt": d}})

    def dispatch_harverster(self,storage_data):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost')) #TODO

        channel = connection.channel()

        channel.queue_declare(queue=storage_data['provider'])
        channel.basic_publish(exchange='',
                              routing_key=storage_data['provider'],
                              body=json.dumps(storage_data, default=json_util.default))
        connection.close()
        self._log_event('foreman', 'dispatch harvester', storage_data)

    def _log_event(self, actor,  event_name, data):
        event_document = {}
        event_document['timestamp'] = datetime.datetime.now()
        event_document['actor'] = actor
        event_document['event_name'] = event_name
        event_document['data'] = data
        self.db['events_log'].insert(event_document)

def main():
    persistence = PersistenceManager()
    persistence._log_event('foreman', 'started', {})
    storages = persistence.find_storage_to_update()
    persistence._log_event('foreman', 'storage check', {'number_of_storage':storages.count()})
    for storage in storages:
        persistence.dispatch_harverster(storage)
    persistence._log_event('foreman', 'terminated', {})

if __name__ == '__main__':
    main()

