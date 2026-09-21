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

from unittest import mock

from django.test import RequestFactory
import pytest

from barbican_ui.content.secrets import forms


def _stored_payload(typed):
    request = RequestFactory().post('/')
    form = forms.CreateSecretForm(request, data={
        'name': 'secret', 'secret_type': 'opaque', 'payload': typed,
        'payload_content_type': 'text/plain',
    })
    assert form.is_valid(), form.errors

    with mock.patch.object(forms.barbican, 'secret_create',
                           return_value='ref') as secret_create, \
            mock.patch.object(forms.messages, 'success'):
        form.handle(request, form.cleaned_data)

    return secret_create.call_args.kwargs['payload']


@pytest.mark.parametrize('typed', [
    '  pass phrase  ', 'key\n', '\tindented', '   ', 'plain',
])
def test_payload_is_stored_as_typed(typed):
    assert _stored_payload(typed) == typed


def test_an_empty_payload_creates_a_metadata_only_secret():
    assert _stored_payload('') is None
