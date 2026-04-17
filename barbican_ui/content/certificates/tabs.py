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


class OverviewTab(tabs.Tab):
    name = _('Overview')
    slug = 'overview'
    template_name = 'barbican_ui/certificates/_detail_overview.html'

    def get_context_data(self, request):
        return {'certificate': self.tab_group.kwargs['certificate']}


class CertificateDetailTabs(tabs.TabGroup):
    slug = 'certificate_details'
    tabs = (OverviewTab,)
    sticky = True
