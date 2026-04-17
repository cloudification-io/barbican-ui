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


class CreateSecret(tables.LinkAction):
    name = 'create'
    verbose_name = _('Create Secret')
    url = 'horizon:project:barbican_secrets:create'
    classes = ('ajax-modal',)
    icon = 'plus'
    policy_rules = (('key-manager', 'secret:post'),)


class DeleteSecret(tables.DeleteAction):
    help_text = _('Deleted secrets cannot be recovered.')
    policy_rules = (('key-manager', 'secret:delete'),)

    @staticmethod
    def action_present(count):
        return ngettext_lazy('Delete Secret', 'Delete Secrets', count)

    @staticmethod
    def action_past(count):
        return ngettext_lazy('Deleted Secret', 'Deleted Secrets', count)

    def delete(self, request, obj_id):
        # obj_id is UUID — reconstruct full href for the API call
        ref = barbican.build_ref(request, 'secrets', obj_id)
        barbican.secret_delete(request, ref)


class RevealPayload(tables.LinkAction):
    name = 'reveal'
    verbose_name = _('Reveal Payload')
    classes = ('ajax-modal',)
    icon = 'eye'
    policy_rules = (('key-manager', 'secret:get'),)

    def get_link_url(self, secret):
        uuid = barbican.ref_to_uuid(secret.secret_ref)
        return reverse('horizon:project:barbican_secrets:reveal', args=[uuid])


class ManageACL(tables.LinkAction):
    name = 'manage_acl'
    verbose_name = _('Manage ACL')
    classes = ('ajax-modal',)
    icon = 'lock'
    policy_rules = (('key-manager', 'secret:get'),)

    def get_link_url(self, secret):
        uuid = barbican.ref_to_uuid(secret.secret_ref)
        # ACL view is registered inside the barbican_secrets URL namespace
        # under the name 'acl' — see content/secrets/urls.py
        return reverse('horizon:project:barbican_secrets:acl', args=[uuid])


class SecretFilterAction(tables.FilterAction):
    name = 'filter_secrets'
    verbose_name = _('Filter Secrets')
    filter_type = 'query'
    filterparam = 'filter_secrets'


class SecretsTable(tables.DataTable):

    name = tables.Column(
        'name',
        verbose_name=_('Name'),
        link='horizon:project:barbican_secrets:detail',
        empty_value=_('(no name)'),
    )
    secret_type = tables.Column(
        'secret_type',
        verbose_name=_('Type'),
        empty_value=_('opaque'),
    )
    algorithm = tables.Column(
        'algorithm',
        verbose_name=_('Algorithm'),
        empty_value=_('—'),
    )
    bit_length = tables.Column(
        'bit_length',
        verbose_name=_('Bit Length'),
        empty_value=_('—'),
    )
    mode = tables.Column(
        'mode',
        verbose_name=_('Mode'),
        empty_value=_('—'),
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
        # Return UUID only — Horizon uses this for link= columns and
        # passes it as obj_id to delete(). Never return the full href.
        return barbican.ref_to_uuid(secret.secret_ref)

    def get_object_display(self, secret):
        return secret.name or barbican.ref_to_uuid(secret.secret_ref)

    class Meta:
        name = 'secrets'
        verbose_name = _('Secret')
        verbose_name_plural = _('Secrets')
        table_actions = (CreateSecret, DeleteSecret, SecretFilterAction)
        row_actions = (RevealPayload, ManageACL, DeleteSecret)
