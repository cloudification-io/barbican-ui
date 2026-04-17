# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

import datetime
import logging

from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from barbican_ui.api import barbican

LOG = logging.getLogger(__name__)

SECRET_TYPES = (
    ('opaque', _('Opaque (arbitrary bytes)')),
    ('symmetric', _('Symmetric Key')),
    ('public', _('Public Key')),
    ('private', _('Private Key')),
    ('passphrase', _('Passphrase')),
    ('certificate', _('Certificate')),
)

ALGORITHMS = (
    ('', _('— Not Specified —')),
    ('aes', 'AES'),
    ('des', '3DES'),
    ('rsa', 'RSA'),
    ('ec', 'EC (Elliptic Curve)'),
    ('hmac', 'HMAC'),
)

BIT_LENGTHS = (
    ('', _('— Not Specified —')),
    (128, '128'),
    (192, '192'),
    (256, '256'),
    (384, '384'),
    (521, '521'),
    (1024, '1024'),
    (2048, '2048'),
    (4096, '4096'),
)

MODES = (
    ('', _('— Not Specified —')),
    ('cbc', 'CBC'),
    ('cfb', 'CFB'),
    ('ecb', 'ECB'),
    ('ctr', 'CTR'),
    ('gcm', 'GCM'),
)

PAYLOAD_CONTENT_TYPES = (
    ('text/plain', _('Plain text  (text/plain)')),
    ('application/octet-stream', _('Binary  (application/octet-stream)')),
    ('application/pkcs8', _('PKCS#8 – Private Key')),
    (
        'application/pkix-cert',
        _('X.509 Certificate DER  (application/pkix-cert)'),
    ),
    ('application/pkcs10', _('PKCS#10 – CSR')),
)


class CreateSecretForm(forms.SelfHandlingForm):
    """Form to store a new secret in Barbican."""

    # ---- Identity -------------------------------------------------------
    name = forms.CharField(
        label=_('Name'),
        required=False,
        max_length=255,
        help_text=_('Optional human-readable label.'),
    )
    secret_type = forms.ChoiceField(
        label=_('Secret Type'),
        choices=SECRET_TYPES,
        initial='opaque',
        required=True,
    )

    # ---- Cryptographic metadata -----------------------------------------
    algorithm = forms.ChoiceField(
        label=_('Algorithm'),
        choices=ALGORITHMS,
        required=False,
    )
    bit_length = forms.ChoiceField(
        label=_('Bit Length'),
        choices=BIT_LENGTHS,
        required=False,
    )
    mode = forms.ChoiceField(
        label=_('Mode'),
        choices=MODES,
        required=False,
    )

    # ---- Payload --------------------------------------------------------
    payload = forms.CharField(
        label=_('Payload'),
        required=False,
        widget=forms.widgets.Textarea(attrs={'rows': 6}),
        help_text=_(
            'The secret value. Leave blank to create a metadata-only secret.'
        ),
    )
    payload_content_type = forms.ChoiceField(
        label=_('Payload Content Type'),
        choices=PAYLOAD_CONTENT_TYPES,
        initial='text/plain',
        required=False,
    )

    # ---- Lifecycle ------------------------------------------------------
    expiration = forms.CharField(
        label=_('Expiration (UTC)'),
        required=False,
        max_length=32,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DDTHH:MM:SS'}),
        help_text=_('Leave blank for no expiration.'),
    )

    def clean_expiration(self):
        value = (self.cleaned_data.get('expiration') or '').strip()
        if not value:
            return None
        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'):
            try:
                return datetime.datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise forms.ValidationError(
            _('Enter a datetime as YYYY-MM-DDTHH:MM:SS.')
        )

    def clean_bit_length(self):
        value = self.cleaned_data.get('bit_length', '')
        if value == '' or value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def handle(self, request, data):
        try:
            payload = (data.get('payload') or '').strip() or None
            ref = barbican.secret_create(
                request,
                name=data.get('name') or None,
                payload=payload,
                payload_content_type=(
                    data.get('payload_content_type') or 'text/plain'
                ) if payload else None,
                algorithm=data.get('algorithm') or None,
                bit_length=data.get('bit_length'),
                mode=data.get('mode') or None,
                secret_type=data.get('secret_type', 'opaque'),
                expiration=data.get('expiration'),
            )
            label = data.get('name') or barbican.ref_to_uuid(ref)
            messages.success(
                request,
                _('Secret "%s" was successfully created.') % label,
            )
            return True
        except Exception as exc:
            exceptions.handle(request, _('Unable to create secret: %s') % exc)
            return False
