# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# _94_barbican_certificates.py
#
# Registers the "Certificates" panel into the "Key Manager" panel group.
# The group is created by _91_barbican_secrets.py which must also be present.

PANEL = 'barbican_certificates'
PANEL_DASHBOARD = 'project'
PANEL_GROUP = 'key_manager'
ADD_PANEL = 'barbican_ui.content.certificates.panel.Certificates'
