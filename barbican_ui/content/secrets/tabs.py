# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

import logging

from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import tabs

from barbican_ui.api import barbican

LOG = logging.getLogger(__name__)


class OverviewTab(tabs.Tab):
    name = _('Overview')
    slug = 'overview'
    template_name = 'barbican_ui/secrets/_detail_overview.html'

    def get_context_data(self, request):
        return {'secret': self.tab_group.kwargs['secret']}


class MetadataTab(tabs.Tab):
    name = _('Metadata')
    slug = 'metadata'
    template_name = 'barbican_ui/secrets/_detail_metadata.html'

    def get_context_data(self, request):
        secret = self.tab_group.kwargs['secret']
        metadata = {}
        try:
            metadata = barbican.secret_metadata_get(
                request, secret.secret_ref
            )
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve metadata.'),
                              ignore=True)
        return {'secret': secret, 'metadata': metadata}


class SecretDetailTabs(tabs.TabGroup):
    slug = 'secret_details'
    tabs = (OverviewTab, MetadataTab)
    sticky = True
