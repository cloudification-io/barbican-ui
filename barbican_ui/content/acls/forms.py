# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

"""ACL forms.

ACLs are not a top-level panel — they appear as modal actions invoked
from the Secrets and Containers detail pages.
"""

import logging

from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from barbican_ui.api import barbican

LOG = logging.getLogger(__name__)


class ManageACLForm(forms.SelfHandlingForm):
    """Set or replace the 'read' ACL on a secret or container."""

    # Hidden field carries the full Barbican entity href.
    entity_ref = forms.CharField(widget=forms.HiddenInput)

    project_access = forms.BooleanField(
        label=_('Allow Project-Wide Access'),
        required=False,
        initial=True,
        help_text=_(
            'When enabled, all members of the current project can read '
            'this resource without being listed individually below.'
        ),
    )
    users = forms.CharField(
        label=_('Allowed User IDs  (one per line)'),
        required=False,
        widget=forms.widgets.Textarea(attrs={'rows': 5}),
        help_text=_(
            'Keystone user UUIDs to grant explicit read access. '
            'Leave blank to rely solely on project-wide access.'
        ),
    )

    def handle(self, request, data):
        try:
            user_list = [
                u.strip()
                for u in (data.get('users') or '').splitlines()
                if u.strip()
            ]
            barbican.acl_submit(
                request,
                entity_ref=data['entity_ref'],
                users=user_list,
                project_access=bool(data.get('project_access', True)),
                operation_type='read',
            )
            messages.success(request, _('ACL updated successfully.'))
            return True
        except Exception as exc:
            exceptions.handle(
                request, _('Unable to update ACL: %s') % exc
            )
            return False


class DeleteACLForm(forms.SelfHandlingForm):
    """Remove all ACL entries from a secret or container."""

    entity_ref = forms.CharField(widget=forms.HiddenInput)

    def handle(self, request, data):
        try:
            barbican.acl_delete(request, data['entity_ref'])
            messages.success(request, _('ACL removed successfully.'))
            return True
        except Exception as exc:
            exceptions.handle(
                request, _('Unable to remove ACL: %s') % exc
            )
            return False
