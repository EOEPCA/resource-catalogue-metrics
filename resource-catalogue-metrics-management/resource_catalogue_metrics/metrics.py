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
from typing import Union
from urllib.parse import urlparse

import click
import paho.mqtt.client as mqtt
import requests

from resource_catalogue_metrics.env import BROKER_URL
from resource_catalogue_metrics import cli_options

LOGGER = logging.getLogger(__name__)


class MetricsAnalyzer:
    def __init__(self, url: str):
        """
        Initializer

        :param url: resource catalogue URL
        :returns: `resource_catalogue_metrics.metrics.MetricsAnalyzer`
        """

        self.url = url
        self.broker = None

        _broker = urlparse(BROKER_URL)
        self.broker = mqtt.Client()
        self.broker.username_pw_set(_broker.username, _broker.password)
        self.broker.connect(_broker.hostname, _broker.port, 60)
        self.broker.loop_start()

    def analyze(self) -> None:
        """
        Analyze catalogue metadata records archive

        :returns: `None`
        """

        self._analyze_collections_total()

    def _analyze_collections_total(self) -> None:
        """
        Analyze total collections

        - resource_catalogue_collections_total

        :returns: `None`
        """

        url_ = f'{self.url}/collections'
        response = requests.get(url_).json()
        collections = response['collections']
        self._publish_metric('resource-catalogue-metrics/metrics/resource_catalogue_collections_total',  # noqa
                             [self.url], len(collections))

    def _publish_metric(self, topic: str, labels: list,
                        value: Union[int, float]) -> None:
        """
        Publish metric

        :param topic: `str` of internal topic
        :param labels: `list` of metric labels
        :param value: `int` or `float` of value
        """

        message = {
            'labels': labels,
            'value': value
        }

        self.broker.publish(topic, json.dumps(message))

    def __repr__(self):
        return '<MetricsAnalyzer>'


@click.group()
def metrics():
    """Resource Catalogue metrics utilities"""

    pass


@click.command()
@click.pass_context
@click.option('-u', '--url', help='URL of Catalogue endpoint')
@cli_options.OPTION_VERBOSITY
def analyze(ctx, url, verbosity='NOTSET'):
    """Analyze Resource Catalogue"""

    if url is None:
        msg = '-u/--url required'
        raise click.ClickException(msg)

    click.echo(f'Analyzing {url}')
    ma = MetricsAnalyzer(url)
    ma.analyze()
    ma.broker.disconnect()
    ma.broker.loop_stop()

    click.echo('Done')


metrics.add_command(analyze)
