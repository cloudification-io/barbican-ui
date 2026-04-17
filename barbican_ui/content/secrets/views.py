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
from barbican_ui.content.secrets import forms
from barbican_ui.content.secrets import tables
from barbican_ui.content.secrets import tabs as secret_tabs

LOG = logging.getLogger(__name__)


class IndexView(horizon_tables.DataTableView):
    table_class = tables.SecretsTable
    template_name = 'barbican_ui/secrets/index.html'
    page_title = _('Secrets')

    def get_data(self):
        try:
            return barbican.secret_list(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve secrets list.'))
            return []


class DetailView(horizon_tabs.TabView):
    tab_group_class = secret_tabs.SecretDetailTabs
    template_name = 'barbican_ui/secrets/detail.html'
    page_title = _('Secret Details')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        secret = self._get_secret()
        context['secret'] = secret
        context['url'] = reverse('horizon:project:barbican_secrets:index')
        if secret:
            context['page_title'] = (
                secret.name or barbican.ref_to_uuid(secret.secret_ref)
            )
        return context

    def _get_secret(self):
        if not hasattr(self, '_secret'):
            ref = barbican.build_ref(
                self.request, 'secrets', self.kwargs['secret_id']
            )
            try:
                self._secret = barbican.secret_get(self.request, ref)
            except Exception:
                exceptions.handle(
                    self.request,
                    _('Unable to retrieve secret details.'),
                    redirect=reverse(
                        'horizon:project:barbican_secrets:index'
                    ),
                )
                self._secret = None
        return self._secret

    def get_tabs(self, request, *args, **kwargs):
        return self.tab_group_class(
            request, secret=self._get_secret(), **kwargs
        )


class CreateView(horizon_forms.ModalFormView):
    """Create a new secret in a Horizon modal.

    ``template_name`` is used on direct navigation.
    ``ajax_template_name`` is used when Horizon opens the AJAX modal.
    """
    form_class = forms.CreateSecretForm
    form_id = 'create_secret_form'
    modal_header = _('Create Secret')
    submit_label = _('Create Secret')
    submit_url = reverse_lazy('horizon:project:barbican_secrets:create')
    template_name = 'barbican_ui/secrets/create.html'
    ajax_template_name = 'barbican_ui/secrets/_create.html'
    page_title = _('Create Secret')
    success_url = reverse_lazy('horizon:project:barbican_secrets:index')


class _RevealForm(horizon_forms.SelfHandlingForm):
    """No-op form — RevealView is display-only, handle() just returns True."""

    def handle(self, request, data):
        return True


class RevealView(horizon_forms.ModalFormView):
    """Display-only modal showing a secret's decrypted payload.

    template_name      -> outer page (extends base.html)
    ajax_template_name -> modal fragment (extends _modal_form.html)
    """
    form_class = _RevealForm
    form_id = 'reveal_secret_form'
    modal_header = _('Secret Payload')
    template_name = 'barbican_ui/secrets/reveal.html'
    ajax_template_name = 'barbican_ui/secrets/_reveal.html'
    page_title = _('Reveal Secret')
    success_url = reverse_lazy('horizon:project:barbican_secrets:index')

    def get_submit_url(self):
        return reverse(
            'horizon:project:barbican_secrets:reveal',
            args=[self.kwargs['secret_id']],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submit_url'] = self.get_submit_url()
        ref = barbican.build_ref(
            self.request, 'secrets', self.kwargs['secret_id']
        )
        try:
            context['payload'] = barbican.secret_get_payload(
                self.request, ref
            )
        except Exception:
            exceptions.handle(
                self.request,
                _('Unable to retrieve payload.'),
                ignore=True,
            )
            context['payload'] = None
        return context
