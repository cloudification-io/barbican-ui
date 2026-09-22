# Copyright 2026 Cloudification GmbH
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

import datetime
from types import SimpleNamespace
from unittest import mock

from barbicanclient.v1 import orders
from barbicanclient.v1 import secrets
from django.test import RequestFactory
import pytest

from barbican_ui.api import barbican
from barbican_ui.content.certificates import forms as certificate_forms
from barbican_ui.content.orders import forms as order_forms
from barbican_ui.content.secrets import forms as secret_forms

REF = ('http://barbican.example.com:9311/v1/%s/'
       '11111111-1111-1111-1111-111111111111')

SECRET = (secret_forms.CreateSecretForm,
          {'name': 'secret', 'secret_type': 'opaque', 'payload': 'p',
           'payload_content_type': 'text/plain'})
CERTIFICATE = (certificate_forms.StoreCertificateForm,
               {'name': 'cert',
                'certificate_pem': '-----BEGIN CERTIFICATE-----\nMIIB\n'
                                   '-----END CERTIFICATE-----'})
KEY_ORDER = (order_forms.CreateOrderForm,
             {'name': 'order', 'order_type': 'key', 'algorithm': 'aes',
              'bit_length': '256'})


def _sent_expiration(form_class, data, typed):
    """Submit the form against the real client and return what it posts."""
    http = mock.Mock()
    http.post.return_value = {'secret_ref': REF % 'secrets',
                              'order_ref': REF % 'orders'}
    client = SimpleNamespace(secrets=secrets.SecretManager(http),
                             orders=orders.OrderManager(http))

    request = RequestFactory().post('/')
    form = form_class(request, data=dict(data, expiration=typed))
    assert form.is_valid(), form.errors

    with mock.patch.object(barbican, 'barbicanclient', return_value=client), \
            mock.patch('horizon.messages.success'):
        assert form.handle(request, form.cleaned_data) is True

    body = http.post.call_args.kwargs['json']
    return body.get('meta', body).get('expiration')


@pytest.mark.parametrize('form_class,data', [
    SECRET, CERTIFICATE, KEY_ORDER,
], ids=['secret', 'certificate', 'key-order'])
@pytest.mark.parametrize('typed,expected', [
    ('2030-01-02T03:04:05', datetime.datetime(
        2030, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc)),
    ('2030-01-02', datetime.datetime(
        2030, 1, 2, tzinfo=datetime.timezone.utc)),
])
def test_expiration_reaches_barbican_as_utc(form_class, data, typed,
                                            expected):
    sent = _sent_expiration(form_class, data, typed)

    assert sent == expected


@pytest.mark.parametrize('form_class,data', [
    SECRET, CERTIFICATE, KEY_ORDER,
], ids=['secret', 'certificate', 'key-order'])
def test_a_blank_expiration_is_not_sent(form_class, data):
    assert _sent_expiration(form_class, data, '') is None
