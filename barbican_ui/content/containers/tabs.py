# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

from django.utils.translation import gettext_lazy as _

from horizon import tabs

from barbican_ui.api import barbican


class OverviewTab(tabs.Tab):
    name = _('Overview')
    slug = 'overview'
    template_name = 'barbican_ui/containers/_detail_overview.html'

    def get_context_data(self, request):
        return {'container': self.tab_group.kwargs['container']}


class SecretsTab(tabs.Tab):
    name = _('Secrets')
    slug = 'secrets'
    template_name = 'barbican_ui/containers/_detail_secrets.html'

    def get_context_data(self, request):
        container = self.tab_group.kwargs['container']
        secret_refs = barbican.container_secret_refs(container)
        return {'container': container, 'secret_refs': secret_refs}


class ContainerDetailTabs(tabs.TabGroup):
    slug = 'container_details'
    tabs = (OverviewTab, SecretsTab)
    sticky = True
