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


def _container_type(container):
    """Return the container type string safely.

    barbicanclient Container objects store type as 'container_type' internally
    but expose it via the 'container_type' property (not 'type').
    We try both attributes and fall back to 'generic'.
    """
    for attr in ('container_type', '_container_type', 'type'):
        val = getattr(container, attr, None)
        if val:
            return val
    return 'generic'


def _secret_count(container):
    """Return the number of secrets in a container safely.

    secret_refs on a barbicanclient Container object is a dict-like of
    {name: SecretRef}.  We use len() on it; fall back to 0 on any error.
    """
    try:
        refs = getattr(container, 'secret_refs', None)
        if refs is None:
            return 0
        return len(refs)
    except Exception:
        return 0


class CreateContainer(tables.LinkAction):
    name = 'create'
    verbose_name = _('Create Container')
    url = 'horizon:project:barbican_containers:create'
    classes = ('ajax-modal',)
    icon = 'plus'
    policy_rules = (('key-manager', 'containers:post'),)


class DeleteContainer(tables.DeleteAction):
    help_text = _('Deleted containers cannot be recovered.')
    policy_rules = (('key-manager', 'containers:delete'),)

    @staticmethod
    def action_present(count):
        return ngettext_lazy('Delete Container', 'Delete Containers', count)

    @staticmethod
    def action_past(count):
        return ngettext_lazy('Deleted Container', 'Deleted Containers', count)

    def delete(self, request, obj_id):
        # obj_id is the UUID; reconstruct full href for the API call
        ref = barbican.build_ref(request, 'containers', obj_id)
        barbican.container_delete(request, ref)


class ManageACL(tables.LinkAction):
    name = 'manage_acl'
    verbose_name = _('Manage ACL')
    url = 'horizon:project:barbican_containers:acl'
    classes = ('ajax-modal',)
    icon = 'lock'
    policy_rules = (('key-manager', 'containers:get'),)

    def get_link_url(self, container):
        uuid = barbican.ref_to_uuid(container.container_ref)
        return reverse(
            'horizon:project:barbican_containers:acl',
            args=[uuid],
        )


class ContainerFilterAction(tables.FilterAction):
    name = 'filter_containers'
    verbose_name = _('Filter Containers')
    filter_type = 'query'
    filterparam = 'filter_containers'


class ContainersTable(tables.DataTable):

    name = tables.Column(
        'name',
        verbose_name=_('Name'),
        link='horizon:project:barbican_containers:detail',
        empty_value=_('(no name)'),
    )
    container_type = tables.Column(
        _container_type,
        verbose_name=_('Type'),
        empty_value=_('generic'),
    )
    status = tables.Column(
        'status',
        verbose_name=_('Status'),
    )
    secret_count = tables.Column(
        _secret_count,
        verbose_name=_('Secrets'),
    )
    created = tables.Column(
        'created',
        verbose_name=_('Created'),
    )

    def get_object_id(self, container):
        # Return UUID only — never the full href
        return barbican.ref_to_uuid(container.container_ref)

    def get_object_display(self, container):
        return container.name or barbican.ref_to_uuid(container.container_ref)

    class Meta:
        name = 'containers'
        verbose_name = _('Container')
        verbose_name_plural = _('Containers')
        table_actions = (
            CreateContainer, DeleteContainer, ContainerFilterAction
        )
        row_actions = (ManageACL, DeleteContainer)
