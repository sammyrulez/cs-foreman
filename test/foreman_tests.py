import datetime
from pymongo import MongoClient

PROVIDER = 'TEST_PROVIDER'

__author__ = 'sam'

import unittest
import pika
from foreman import demon
from bson import json_util
import json


class ForemanCase(unittest.TestCase):
    def setUp(self):
        mongodb_host = 'localhost'
        mongodb_port = 27017
        mongodb_name = 'foreman'
        self.client = MongoClient(mongodb_host, mongodb_port)
        self.db = self.client[mongodb_name]
        d = datetime.datetime.now() - datetime.timedelta(minutes=18)
        self.db['storages'].insert({"last-updated": d, 'provider': PROVIDER})
        demon.main()


def tearDown(self):
    self.db['storages'].remove()
    self.db['events_log'].remove()


def test_logs_check(self):
    logs = self.db['events_log'].find()
    self.assertEquals(4, logs.count())


def test_queue(self):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=PROVIDER)

    method_frame, header_frame, body = channel.basic_get(queue=PROVIDER)
    if method_frame.NAME == 'Basic.GetEmpty':
        connection.close()
        self.fail('NO msg on queue')
    else:
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        connection.close()
        data = json.loads(body, object_hook=json_util.object_hook)
        self.assertTrue('provider' in data)


if __name__ == '__main__':
    unittest.main()
