# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

import logging

from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from barbican_ui.api import barbican

LOG = logging.getLogger(__name__)

CONTAINER_TYPES = (
    ('generic', _('Generic – arbitrary named secret refs')),
    ('certificate', _('Certificate – cert + private key + intermediates')),
    ('rsa', _('RSA – public key + private key + passphrase')),
)


class CreateContainerForm(forms.SelfHandlingForm):
    """Create a new Barbican container."""

    name = forms.CharField(
        label=_('Name'),
        required=False,
        max_length=255,
        help_text=_('Optional human-readable label.'),
    )
    container_type = forms.ChoiceField(
        label=_('Container Type'),
        choices=CONTAINER_TYPES,
        initial='generic',
        required=True,
    )

    # ---- Generic --------------------------------------------------------
    secret_refs = forms.CharField(
        label=_('Secret References  (Generic)'),
        required=False,
        widget=forms.widgets.Textarea(attrs={'rows': 4}),
        help_text=_(
            'One  label=secret_href  per line.\n'
            'Example:\n'
            '  my_key=https://barbican/v1/secrets/uuid'
        ),
    )

    # ---- Certificate ----------------------------------------------------
    certificate_ref = forms.CharField(
        label=_('Certificate Secret Ref'),
        required=False,
        max_length=512,
    )
    private_key_ref = forms.CharField(
        label=_('Private Key Secret Ref'),
        required=False,
        max_length=512,
    )
    private_key_passphrase_ref = forms.CharField(
        label=_('Private Key Passphrase Secret Ref'),
        required=False,
        max_length=512,
    )
    intermediates_ref = forms.CharField(
        label=_('Intermediates Secret Ref'),
        required=False,
        max_length=512,
    )

    # ---- RSA ------------------------------------------------------------
    public_key_ref = forms.CharField(
        label=_('Public Key Secret Ref'),
        required=False,
        max_length=512,
    )
    rsa_private_key_ref = forms.CharField(
        label=_('RSA Private Key Secret Ref'),
        required=False,
        max_length=512,
    )
    rsa_passphrase_ref = forms.CharField(
        label=_('RSA Passphrase Secret Ref'),
        required=False,
        max_length=512,
    )

    def _parse_generic_refs(self, raw):
        secrets = {}
        for line in (raw or '').splitlines():
            line = line.strip()
            if '=' in line:
                label, _, ref = line.partition('=')
                label = label.strip()
                ref = ref.strip()
                if label and ref:
                    secrets[label] = ref
        return secrets

    def handle(self, request, data):
        try:
            ctype = data['container_type']
            name = data.get('name') or None
            secrets = {}

            if ctype == 'generic':
                secrets = self._parse_generic_refs(data.get('secret_refs'))

            elif ctype == 'certificate':
                for role, field in (
                    ('certificate', 'certificate_ref'),
                    ('private_key', 'private_key_ref'),
                    ('private_key_passphrase', 'private_key_passphrase_ref'),
                    ('intermediates', 'intermediates_ref'),
                ):
                    val = data.get(field, '').strip()
                    if val:
                        secrets[role] = val

            elif ctype == 'rsa':
                for role, field in (
                    ('public_key', 'public_key_ref'),
                    ('private_key', 'rsa_private_key_ref'),
                    ('private_key_passphrase', 'rsa_passphrase_ref'),
                ):
                    val = data.get(field, '').strip()
                    if val:
                        secrets[role] = val

            ref = barbican.container_create(
                request,
                container_type=ctype,
                name=name,
                secrets=secrets,
            )
            label = name or barbican.ref_to_uuid(ref)
            messages.success(
                request,
                _('Container "%s" was successfully created.') % label,
            )
            return True
        except Exception as exc:
            exceptions.handle(
                request, _('Unable to create container: %s') % exc
            )
            return False
