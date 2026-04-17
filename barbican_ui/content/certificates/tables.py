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
from django.utils.translation import ngettext_lazy

from horizon import tables

from barbican_ui.api import barbican

LOG = logging.getLogger(__name__)


class StoreCertificate(tables.LinkAction):
    name = 'store'
    verbose_name = _('Store Certificate')
    url = 'horizon:project:barbican_certificates:create'
    classes = ('ajax-modal',)
    icon = 'plus'
    policy_rules = (('key-manager', 'secret:post'),)


class DeleteCertificate(tables.DeleteAction):
    help_text = _('Deleted certificates cannot be recovered.')
    policy_rules = (('key-manager', 'secret:delete'),)

    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            'Delete Certificate', 'Delete Certificates', count
        )

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            'Deleted Certificate', 'Deleted Certificates', count
        )

    def delete(self, request, obj_id):
        # obj_id is UUID; certificates are stored as secrets
        ref = barbican.build_ref(request, 'secrets', obj_id)
        barbican.secret_delete(request, ref)


class DownloadCertificate(tables.LinkAction):
    name = 'download'
    verbose_name = _('Download PEM')
    icon = 'download-alt'
    policy_rules = (('key-manager', 'secret:get'),)

    def get_link_url(self, secret):
        uuid = barbican.ref_to_uuid(secret.secret_ref)
        return reverse(
            'horizon:project:barbican_certificates:download',
            args=[uuid],
        )


class CertificateFilterAction(tables.FilterAction):
    name = 'filter_certs'
    verbose_name = _('Filter Certificates')
    filter_type = 'query'
    filterparam = 'filter_certs'


class CertificatesTable(tables.DataTable):

    name = tables.Column(
        'name',
        verbose_name=_('Name'),
        link='horizon:project:barbican_certificates:detail',
        empty_value=_('(no name)'),
    )
    status = tables.Column(
        'status',
        verbose_name=_('Status'),
    )
    expiration = tables.Column(
        'expiration',
        verbose_name=_('Expiration'),
        empty_value=_('Never'),
    )
    created = tables.Column(
        'created',
        verbose_name=_('Created'),
    )

    def get_object_id(self, secret):
        # Return UUID only
        return barbican.ref_to_uuid(secret.secret_ref)

    def get_object_display(self, secret):
        return secret.name or barbican.ref_to_uuid(secret.secret_ref)

    class Meta:
        name = 'certificates'
        verbose_name = _('Certificate')
        verbose_name_plural = _('Certificates')
        table_actions = (
            StoreCertificate, DeleteCertificate, CertificateFilterAction
        )
        row_actions = (DownloadCertificate, DeleteCertificate)
