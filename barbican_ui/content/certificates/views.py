# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.http import content_disposition_header
from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms as horizon_forms
from horizon import messages
from horizon import tables as horizon_tables
from horizon import tabs as horizon_tabs

from barbican_ui.api import barbican
from barbican_ui.content.certificates import forms
from barbican_ui.content.certificates import tables
from barbican_ui.content.certificates import tabs as cert_tabs
from barbican_ui.content import pagination

LOG = logging.getLogger(__name__)


class IndexView(pagination.OffsetPagedView,
                horizon_tables.DataTableView):
    """List all secrets whose secret_type == 'certificate'."""

    table_class = tables.CertificatesTable
    template_name = 'barbican_ui/certificates/index.html'
    page_title = _('Certificates')

    def get_data(self):
        try:
            return self.paginate(barbican.secret_list,
                                 secret_type='certificate')
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve certificates.'))
            return []


class DetailView(horizon_tabs.TabView):
    tab_group_class = cert_tabs.CertificateDetailTabs
    template_name = 'barbican_ui/certificates/detail.html'
    page_title = _('Certificate Details')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cert = self._get_certificate()
        context['certificate'] = cert
        context['certificate_id'] = self.kwargs['certificate_id']
        context['url'] = reverse('horizon:project:barbican_certificates:index')
        if cert:
            context['page_title'] = (
                cert.name or barbican.ref_to_uuid(cert.secret_ref)
            )
        return context

    def _get_certificate(self):
        if not hasattr(self, '_certificate'):
            ref = barbican.build_ref(
                self.request, 'secrets', self.kwargs['certificate_id']
            )
            try:
                self._certificate = barbican.secret_get(self.request, ref)
            except Exception:
                exceptions.handle(
                    self.request,
                    _('Unable to retrieve certificate details.'),
                    redirect=reverse(
                        'horizon:project:barbican_certificates:index'
                    ),
                )
                self._certificate = None
        return self._certificate

    def get_tabs(self, request, *args, **kwargs):
        return self.tab_group_class(
            request, certificate=self._get_certificate(), **kwargs
        )


class CreateView(horizon_forms.ModalFormView):
    form_class = forms.StoreCertificateForm
    form_id = 'store_certificate_form'
    modal_header = _('Store Certificate')
    submit_label = _('Store Certificate')
    submit_url = reverse_lazy('horizon:project:barbican_certificates:create')
    template_name = 'barbican_ui/certificates/create.html'
    ajax_template_name = 'barbican_ui/certificates/_create.html'
    page_title = _('Store Certificate')
    success_url = reverse_lazy('horizon:project:barbican_certificates:index')


class DownloadView(horizon_forms.ModalFormView):
    """Serve a certificate secret as a downloadable .pem file."""

    # Inheriting ModalFormView so Horizon's URL machinery works;
    # we override dispatch to return a file response directly.
    form_class = horizon_forms.SelfHandlingForm
    template_name = 'barbican_ui/certificates/create.html'  # never rendered

    def get(self, request, *args, **kwargs):
        certificate_id = self.kwargs['certificate_id']
        ref = barbican.build_ref(request, 'secrets', certificate_id)
        try:
            secret = barbican.secret_get(request, ref)
            if getattr(secret, 'secret_type', None) != 'certificate':
                messages.error(
                    request,
                    _('The requested secret is not a certificate.'),
                )
                return redirect(
                    'horizon:project:barbican_certificates:index'
                )

            payload = barbican.secret_get_payload(request, ref)
            filename = (secret.name or certificate_id) + '.pem'
            # Ensure payload is a string; some content types return bytes
            if isinstance(payload, bytes):
                payload_data = payload
            else:
                payload_data = payload.encode('utf-8')
            response = HttpResponse(
                payload_data,
                content_type='application/x-pem-file',
            )
            response['Content-Disposition'] = content_disposition_header(
                True, filename
            )
            return response
        except Exception:
            exceptions.handle(
                request,
                _('Unable to download certificate.'),
                redirect=reverse(
                    'horizon:project:barbican_certificates:index'
                ),
            )
