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
from django.utils.translation import gettext_lazy as _

from horizon import forms as horizon_forms

from barbican_ui.api import barbican
from barbican_ui.content.acls import forms

LOG = logging.getLogger(__name__)


class ManageSecretACLView(horizon_forms.ModalFormView):
    """Manage the 'read' ACL for a secret.

    Registered under barbican_secrets namespace as name='acl':
        horizon:project:barbican_secrets:acl
    """
    form_class = forms.ManageACLForm
    form_id = 'manage_secret_acl_form'
    modal_header = _('Manage Secret ACL')
    submit_label = _('Save ACL')
    template_name = 'barbican_ui/acls/manage.html'
    ajax_template_name = 'barbican_ui/acls/_manage.html'
    page_title = _('Manage Secret ACL')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submit_url'] = reverse(
            'horizon:project:barbican_secrets:acl',
            args=[self.kwargs['secret_id']],
        )
        return context

    def get_success_url(self):
        return reverse(
            'horizon:project:barbican_secrets:index',
        )

    def get_initial(self):
        secret_id = self.kwargs['secret_id']
        ref = barbican.build_ref(self.request, 'secrets', secret_id)
        acl = barbican.acl_get(self.request, ref)
        return {
            'entity_ref': ref,
            'users': '\n'.join(acl.get('users') or []),
            'project_access': acl.get('project_access', True),
        }


class ManageContainerACLView(horizon_forms.ModalFormView):
    """Manage the 'read' ACL for a container.

    Registered under barbican_containers namespace as name='acl':
        horizon:project:barbican_containers:acl
    """
    form_class = forms.ManageACLForm
    form_id = 'manage_container_acl_form'
    modal_header = _('Manage Container ACL')
    submit_label = _('Save ACL')
    template_name = 'barbican_ui/acls/manage.html'
    ajax_template_name = 'barbican_ui/acls/_manage.html'
    page_title = _('Manage Container ACL')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submit_url'] = reverse(
            'horizon:project:barbican_containers:acl',
            args=[self.kwargs['container_id']],
        )
        return context

    def get_success_url(self):
        return reverse(
            'horizon:project:barbican_containers:index',
        )

    def get_initial(self):
        container_id = self.kwargs['container_id']
        ref = barbican.build_ref(self.request, 'containers', container_id)
        acl = barbican.acl_get(self.request, ref)
        return {
            'entity_ref': ref,
            'users': '\n'.join(acl.get('users') or []),
            'project_access': acl.get('project_access', True),
        }
