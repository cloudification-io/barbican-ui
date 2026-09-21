# Copyright 2026 Cloudification GmbH
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

from types import SimpleNamespace
from unittest import mock

from django.test import RequestFactory
import pytest

from barbican_ui.content.certificates import views

PEM = '-----BEGIN CERTIFICATE-----\nMIIB\n-----END CERTIFICATE-----\n'


def _download(name, payload=PEM):
    secret = SimpleNamespace(name=name, secret_type='certificate')
    with mock.patch.object(views.barbican, 'secret_get',
                           return_value=secret), \
            mock.patch.object(views.barbican, 'secret_get_payload',
                              return_value=payload):
        return views.DownloadView.as_view()(
            RequestFactory().get('/'), certificate_id='abc')


@pytest.mark.parametrize('payload', [PEM, PEM.encode('utf-8')])
def test_download_serves_the_payload_as_a_pem_attachment(payload):
    response = _download('web', payload)

    assert response.status_code == 200
    assert response.content == PEM.encode('utf-8')
    assert response['Content-Type'] == 'application/x-pem-file'
    assert response['Content-Disposition'] == 'attachment; filename="web.pem"'


def test_download_falls_back_to_the_uuid_for_an_unnamed_secret():
    response = _download(None)

    assert response['Content-Disposition'] == 'attachment; filename="abc.pem"'


def test_download_escapes_quotes_in_the_filename():
    response = _download('a"; filename*=utf-8\'\'evil.exe; x="')

    assert response['Content-Disposition'] == (
        'attachment; filename="a\\"; filename*=utf-8\'\'evil.exe; x=\\".pem"'
    )


def test_download_encodes_a_non_ascii_filename():
    response = _download('сертификат')

    assert response['Content-Disposition'] == (
        "attachment; filename*=utf-8''"
        '%D1%81%D0%B5%D1%80%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%82.pem'
    )
