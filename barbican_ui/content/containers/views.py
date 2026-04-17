# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

import logging

from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms as horizon_forms
from horizon import tables as horizon_tables
from horizon import tabs as horizon_tabs

from barbican_ui.api import barbican
from barbican_ui.content.containers import forms
from barbican_ui.content.containers import tables
from barbican_ui.content.containers import tabs as container_tabs

LOG = logging.getLogger(__name__)


class IndexView(horizon_tables.DataTableView):
    table_class = tables.ContainersTable
    template_name = 'barbican_ui/containers/index.html'
    page_title = _('Containers')

    def get_data(self):
        try:
            return barbican.container_list(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve containers.'))
            return []


class DetailView(horizon_tabs.TabView):
    tab_group_class = container_tabs.ContainerDetailTabs
    template_name = 'barbican_ui/containers/detail.html'
    page_title = _('Container Details')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        container = self._get_container()
        context['container'] = container
        context['url'] = reverse('horizon:project:barbican_containers:index')
        if container:
            context['page_title'] = (
                container.name or
                barbican.ref_to_uuid(container.container_ref)
            )
        return context

    def _get_container(self):
        if not hasattr(self, '_container'):
            ref = barbican.build_ref(
                self.request, 'containers', self.kwargs['container_id']
            )
            try:
                self._container = barbican.container_get(self.request, ref)
            except Exception:
                exceptions.handle(
                    self.request,
                    _('Unable to retrieve container details.'),
                    redirect=reverse(
                        'horizon:project:barbican_containers:index'
                    ),
                )
                self._container = None
        return self._container

    def get_tabs(self, request, *args, **kwargs):
        return self.tab_group_class(
            request, container=self._get_container(), **kwargs
        )


class CreateView(horizon_forms.ModalFormView):
    form_class = forms.CreateContainerForm
    form_id = 'create_container_form'
    modal_header = _('Create Container')
    submit_label = _('Create Container')
    submit_url = reverse_lazy('horizon:project:barbican_containers:create')
    template_name = 'barbican_ui/containers/create.html'
    ajax_template_name = 'barbican_ui/containers/_create.html'
    page_title = _('Create Container')
    success_url = reverse_lazy('horizon:project:barbican_containers:index')
