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

from types import SimpleNamespace
from unittest import mock

from barbicanclient.v1 import orders
from django.test import RequestFactory
import pytest

from barbican_ui.api import barbican
from barbican_ui.content.orders import forms

ORDER_REF = ('http://barbican.example.com:9311/v1/orders/'
             '11111111-1111-1111-1111-111111111111')


def _submitted_order(data):
    """Submit the form against the real order manager, return what it posts."""
    http = mock.Mock()
    http.post.return_value = {'order_ref': ORDER_REF}
    client = SimpleNamespace(orders=orders.OrderManager(http))

    request = RequestFactory().post('/')
    form = forms.CreateOrderForm(request, data=data)
    assert form.is_valid(), form.errors

    with mock.patch.object(barbican, 'barbicanclient', return_value=client), \
            mock.patch('horizon.messages.success'):
        assert form.handle(request, form.cleaned_data) is True

    return http.post.call_args.kwargs['json']


@pytest.mark.parametrize('mode', ['', 'cbc'])
def test_an_asymmetric_order_is_submitted(mode):
    body = _submitted_order({
        'name': 'pair', 'order_type': 'asymmetric', 'algorithm': 'rsa',
        'bit_length': '2048', 'mode': mode,
    })

    assert body['type'] == 'asymmetric'
    assert body['meta']['algorithm'] == 'rsa'
    assert body['meta']['bit_length'] == 2048
    assert 'mode' not in body['meta']


def test_a_key_order_keeps_its_mode():
    body = _submitted_order({
        'name': 'key', 'order_type': 'key', 'algorithm': 'aes',
        'bit_length': '256', 'mode': 'cbc',
    })

    assert body['type'] == 'key'
    assert body['meta']['mode'] == 'cbc'
