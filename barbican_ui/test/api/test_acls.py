# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

from unittest import mock

from barbicanclient.v1 import acls

from barbican_ui.api import barbican

SECRET_REF = ('http://barbican.example.com:9311/v1/secrets/'
              '6d4a3b1c-0c2e-4f0e-9a51-3f6f2f1f7a10')


def _submit(acl, **kwargs):
    client = mock.Mock()
    client.acls.get.return_value = acl
    with mock.patch.object(barbican, 'barbicanclient', return_value=client):
        barbican.acl_submit(mock.sentinel.request, SECRET_REF, **kwargs)


def test_acl_submit_updates_the_existing_operation_acl():
    api = mock.Mock()
    acl = acls.SecretACL(api, SECRET_REF, users=['old'], project_access=True)

    _submit(acl, users=['u1'], project_access=False)

    assert api.put.call_args.kwargs['json'] == {
        'read': {'project-access': False, 'users': ['u1']},
    }


def test_acl_submit_adds_a_missing_operation_acl():
    api = mock.Mock()
    acl = acls.SecretACL(api, SECRET_REF)

    _submit(acl, users=['u1'], project_access=False)

    assert api.put.call_args.kwargs['json'] == {
        'read': {'project-access': False, 'users': ['u1']},
    }
