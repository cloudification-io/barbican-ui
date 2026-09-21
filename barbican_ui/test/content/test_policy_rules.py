# Copyright 2026 Cloudification GmbH
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

import importlib
import inspect

import pytest

# Rule names registered in barbican/common/policies.
BARBICAN_RULES = frozenset([
    'secrets:get', 'secrets:post',
    'secret:get', 'secret:put', 'secret:delete', 'secret:decrypt',
    'secret_acls:get', 'secret_acls:put_patch', 'secret_acls:delete',
    'containers:get', 'containers:post',
    'container:get', 'container:delete',
    'container_acls:get', 'container_acls:put_patch',
    'container_acls:delete',
    'orders:get', 'orders:post', 'orders:put',
    'order:get', 'order:delete',
])

MODULES = [
    'barbican_ui.content.%s.%s' % (panel, module)
    for panel in ('secrets', 'certificates', 'containers', 'orders')
    for module in ('panel', 'tables')
]


def _policy_rules():
    for name in MODULES:
        module = importlib.import_module(name)
        for cls_name, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != name:
                continue
            for scope, rule in getattr(cls, 'policy_rules', None) or ():
                yield pytest.param(scope, rule,
                                   id='%s.%s' % (name.split('.', 2)[2],
                                                 cls_name))


@pytest.mark.parametrize('scope,rule', _policy_rules())
def test_policy_rule_exists_in_barbican(scope, rule):
    assert scope == 'key-manager'
    assert rule in BARBICAN_RULES
