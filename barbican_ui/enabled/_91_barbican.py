# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# _91_barbican.py
#
# This file does two things:
#   1. Creates the "Key Manager" panel group inside the "project" dashboard.
#   2. Registers the "Secrets" panel as the first entry in that group.
#
# Installation (manual):
#   cp barbican_ui/enabled/_91_barbican.py \
#      <horizon>/openstack_dashboard/local/enabled/
#
# Installation (pip): the setup.cfg openstack_dashboard_config entry point
# exposes this package's enabled module to Horizon packaging tools.

# -------------------------------------------------------------------------
# Panel Group  (created by this first enabled file; referenced by the rest)
# -------------------------------------------------------------------------
PANEL_GROUP = 'key_manager'
PANEL_GROUP_NAME = 'Key Manager'
PANEL_GROUP_DASHBOARD = 'project'

# -------------------------------------------------------------------------
# Django / static (only needs to be declared once, in this first file)
# -------------------------------------------------------------------------
ADD_INSTALLED_APPS = ['barbican_ui']
AUTO_DISCOVER_STATIC_FILES = True
