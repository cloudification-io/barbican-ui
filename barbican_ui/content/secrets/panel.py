# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

import horizon


class Secrets(horizon.Panel):
    """Secrets panel under Project > Key Manager."""

    name = 'Secrets'
    slug = 'barbican_secrets'
    icon = 'fa-key'
    permissions = ('openstack.services.key-manager',)
    policy_rules = (('key-manager', 'secret:get'),)
