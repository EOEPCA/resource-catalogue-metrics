###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

import json
import logging
import os
import sys
from urllib.parse import urlparse

import paho.mqtt.client as mqtt_client
from prometheus_client import (
    Gauge, start_http_server, REGISTRY, GC_COLLECTOR,
    PLATFORM_COLLECTOR, PROCESS_COLLECTOR
)

REGISTRY.unregister(GC_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(PROCESS_COLLECTOR)

BROKER_URL = os.environ['RESOURCE_CATALOGUE_METRICS_BROKER_URL']
HTTP_PORT = 8006
LOGGING_LEVEL = os.environ['RESOURCE_CATALOGUE_METRICS_LOGGING_LEVEL']

logging.basicConfig(stream=sys.stdout)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOGGING_LEVEL)

METRIC_COLLECTIONS_TOTAL = Gauge(
    'resource_catalogue_collections_total',
    'Number of collections',
    ['resource-catalogue']
)

METRIC_ITEMS_TOTAL = Gauge(
    'resource_catalogue_items_total',
    'Number of items',
    ['resource-catalogue', 'collection_id']
)

METRIC_ASSETS_TOTAL = Gauge(
    'resource_catalogue_assets_total',
    'Number of assets',
    ['resource-catalogue', 'collection_id']
)


def init_metrics() -> None:
    """
    Initializes metrics on startup

    :returns: `None`
    """

    pass


def collect_metrics() -> None:
    """
    Subscribe to MQTT resource-catalogue-metrics/metrics and collect metrics

    :returns: `None`
    """

    def _sub_connect(client, userdata, flags, rc):
        LOGGER.info('Subscribing to topic resource-catalogue-metrics/metrics/#')  # noqa
        client.subscribe('resource-catalogue-metrics/metrics/#', qos=0)

    def _sub_message(client, userdata, msg):
        LOGGER.debug('Processing message')
        topic = msg.topic
        payload = json.loads(msg.payload)
        labels = payload['labels']
        value = payload.get('value')
        LOGGER.debug(f'Topic: {topic}')
        LOGGER.debug(f"Labels: {payload['labels']}")
        LOGGER.debug(f"Value: {payload.get('labels')}")

        if topic == 'resource-catalogue-metrics/metrics/clear':
            LOGGER.info('Clearing all metrics')
            METRIC_COLLECTIONS_TOTAL.clear()
            METRIC_ITEMS_TOTAL.clear()
            METRIC_ASSETS_TOTAL.clear()
        elif topic == 'resource-catalogue-metrics/metrics/init':
            LOGGER.info('Initializing metrics')
            init_metrics()
        elif topic == 'resource-catalogue-metrics/metrics/collections_total':
            METRIC_COLLECTIONS_TOTAL.labels(*labels).set(value)
        elif topic == 'resource-catalogue-metrics/metrics/items_total':
            METRIC_ITEMS_TOTAL.labels(*labels).set(value)
        elif topic == 'resource-catalogue-metrics/metrics/assets_total':
            METRIC_ASSETS_TOTAL.labels(*labels).set(value)

    url = urlparse(BROKER_URL)

    client_id = 'resource-catalogue-metrics metrics collector'

    try:
        LOGGER.info('Setting up MQTT client')
        client = mqtt_client.Client(client_id)
        client.on_connect = _sub_connect
        client.on_message = _sub_message
        client.username_pw_set(url.username, url.password)
        LOGGER.info(f'Connecting to {url.hostname}')
        client.connect(url.hostname, url.port)
        client.loop_forever()
    except Exception as err:
        LOGGER.error(err)


if __name__ == '__main__':
    LOGGER.info(f'Starting metrics collector server on port {HTTP_PORT}')
    start_http_server(HTTP_PORT)
    init_metrics()
    collect_metrics()
