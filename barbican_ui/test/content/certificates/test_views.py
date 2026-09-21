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

from django.test import RequestFactory
from django.urls import include
from django.urls import path
import pytest

from barbican_ui.content.certificates import views

_project = ([path('project/',
                  include('barbican_ui.content.certificates.urls'))],
            'project')
urlpatterns = [path('', include(([path('', include(_project))], 'horizon')))]


def _certificate():
    return SimpleNamespace(
        name='web', secret_type='certificate', status='ACTIVE',
        secret_ref='http://barbican.example.com:9311/v1/secrets/abc',
        algorithm=None, bit_length=None, mode=None, expiration=None,
        created=None, updated=None, content_types={},
    )


@pytest.mark.urls(__name__)
def test_detail_overview_tab_links_to_the_download_view():
    request = RequestFactory().get('/')
    request.user = SimpleNamespace(has_perms=lambda perms: True)
    view = views.DetailView()
    view.request = request
    view.args = ()
    view.kwargs = {'certificate_id': 'abc'}

    with mock.patch.object(views.barbican, 'secret_get',
                           return_value=_certificate()):
        context = view.get_context_data(certificate_id='abc')
        html = context['tab_group'].get_tabs()[0].render()

    assert 'href="/project/certificates/abc/download/"' in html
