# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

import horizon


class Orders(horizon.Panel):
    """Orders panel under Project > Key Manager."""

    name = 'Orders'
    slug = 'barbican_orders'
    icon = 'fa-list-alt'
    permissions = ('openstack.services.key-manager',)
    policy_rules = (('key-manager', 'orders:get'),)
