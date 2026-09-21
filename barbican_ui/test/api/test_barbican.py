# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from types import SimpleNamespace
from unittest import mock

import pytest

from barbican_ui.api import barbican


def _request_with_catalog(catalog):
    return SimpleNamespace(user=SimpleNamespace(
        service_catalog=catalog,
        token=SimpleNamespace(id='token'), tenant_id='p1'))


def _client(request):
    with mock.patch.object(barbican.ks_session, 'Session') as session, \
            mock.patch.object(barbican.barbican_client, 'Client') as client:
        barbican.barbicanclient(request)
    return session, client


def test_barbicanclient_does_not_log_the_token():
    request = _request_with_catalog([])
    request.user.token.id = 'gAAAA-secret-token'

    with mock.patch.object(barbican, 'LOG') as log:
        _client(request)

    assert log.debug.called
    assert 'gAAAA-secret-token' not in repr(log.mock_calls)


def test_barbicanclient_returns_none_when_key_manager_not_in_catalog(
        settings):
    settings.BARBICAN_ENDPOINT = None
    request = _request_with_catalog([])

    assert barbican.barbicanclient(request) is None


def test_barbicanclient_uses_the_configured_endpoint(settings):
    settings.BARBICAN_ENDPOINT = 'https://barbican.example.com:9311/v1/'

    _, client = _client(_request_with_catalog([]))

    assert client.call_args.kwargs['endpoint'] == (
        'https://barbican.example.com:9311')


def test_barbicanclient_looks_up_the_configured_endpoint_type(settings):
    settings.BARBICAN_ENDPOINT = None
    settings.BARBICAN_ENDPOINT_TYPE = 'internalURL'

    with mock.patch.object(barbican.base, 'url_for',
                           return_value='http://barbican.svc:9311') as url_for:
        _, client = _client(_request_with_catalog([]))

    assert url_for.call_args.kwargs['endpoint_type'] == 'internalURL'
    assert client.call_args.kwargs['endpoint'] == 'http://barbican.svc:9311'


@pytest.mark.parametrize('overrides,verify', [
    ({}, True),
    ({'BARBICAN_CACERT': '/etc/ssl/barbican-ca.pem'},
     '/etc/ssl/barbican-ca.pem'),
    ({'OPENSTACK_SSL_CACERT': '/etc/ssl/ca.pem'}, '/etc/ssl/ca.pem'),
    ({'BARBICAN_CACERT': '/etc/ssl/barbican-ca.pem',
      'OPENSTACK_SSL_CACERT': '/etc/ssl/ca.pem'}, '/etc/ssl/barbican-ca.pem'),
    ({'BARBICAN_INSECURE': True}, False),
    ({'OPENSTACK_SSL_NO_VERIFY': True}, False),
    ({'BARBICAN_INSECURE': True,
      'BARBICAN_CACERT': '/etc/ssl/barbican-ca.pem'}, False),
])
def test_barbicanclient_tls_verification(settings, overrides, verify):
    settings.BARBICAN_INSECURE = False
    settings.BARBICAN_CACERT = None
    settings.OPENSTACK_SSL_NO_VERIFY = False
    settings.OPENSTACK_SSL_CACERT = None
    for name, value in overrides.items():
        setattr(settings, name, value)

    session, _ = _client(_request_with_catalog([]))

    assert session.call_args.kwargs['verify'] == verify
