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

ORDER_TYPES = (
    ('key', _('Symmetric Key')),
    ('asymmetric', _('Asymmetric Key Pair')),
)

KEY_ALGORITHMS = (
    ('aes', 'AES'),
    ('des', '3DES'),
    ('hmac', 'HMAC'),
)

ASYM_ALGORITHMS = (
    ('rsa', 'RSA'),
    ('ec', 'EC (Elliptic Curve)'),
    ('dsa', 'DSA'),
)

ALGORITHMS = KEY_ALGORITHMS + ASYM_ALGORITHMS
KEY_ALGORITHM_VALUES = {value for value, _label in KEY_ALGORITHMS}
ASYM_ALGORITHM_VALUES = {value for value, _label in ASYM_ALGORITHMS}
DEFAULT_PAYLOAD_CONTENT_TYPE = 'application/octet-stream'

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


class CreateOrderForm(forms.SelfHandlingForm):
    """Submit a new key-generation order to Barbican."""

    order_type = forms.ChoiceField(
        label=_('Order Type'),
        choices=ORDER_TYPES,
        required=True,
        help_text=_(
            'Key: generate a symmetric key.  '
            'Asymmetric: generate a key pair stored in a Container.'
        ),
    )

    # ---- Shared: key + asymmetric ---------------------------------------
    name = forms.CharField(
        label=_('Name'),
        required=False,
        max_length=255,
        help_text=_('Optional label for the generated secret.'),
    )
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
        help_text=_('Cipher mode (symmetric keys only).'),
    )
    expiration = forms.CharField(
        label=_('Expiration (UTC)'),
        required=False,
        max_length=32,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DDTHH:MM:SS'}),
    )
    payload_content_type = forms.CharField(
        label=_('Payload Content Type'),
        required=False,
        initial='application/octet-stream',
        max_length=128,
    )

    def _clean_expiration(self, value):
        value = (value or '').strip()
        if not value:
            return None
        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'):
            try:
                return datetime.datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise forms.ValidationError(
            _('Enter expiration as YYYY-MM-DDTHH:MM:SS.')
        )

    def _clean_bit_length(self, value):
        if value == '' or value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def handle(self, request, data):
        try:
            order_type = data['order_type']
            expiration = self._clean_expiration(data.get('expiration'))
            bit_length = self._clean_bit_length(data.get('bit_length'))

            if order_type == 'key':
                algorithm = data.get('algorithm') or 'aes'
                payload_type = data.get('payload_content_type')
                payload_content_type = (
                    payload_type or DEFAULT_PAYLOAD_CONTENT_TYPE
                )
                if algorithm not in KEY_ALGORITHM_VALUES:
                    raise forms.ValidationError(
                        _('Symmetric key orders require AES, 3DES, or HMAC.')
                    )
                ref = barbican.order_create_key(
                    request,
                    name=data.get('name') or None,
                    algorithm=algorithm,
                    bit_length=bit_length or 256,
                    mode=data.get('mode') or None,
                    payload_content_type=payload_content_type,
                    expiration=expiration,
                )

            elif order_type == 'asymmetric':
                algorithm = data.get('algorithm') or 'rsa'
                payload_type = data.get('payload_content_type')
                payload_content_type = (
                    payload_type or DEFAULT_PAYLOAD_CONTENT_TYPE
                )
                if algorithm not in ASYM_ALGORITHM_VALUES:
                    raise forms.ValidationError(
                        _('Asymmetric key orders require RSA, EC, or DSA.')
                    )
                ref = barbican.order_create_asymmetric(
                    request,
                    name=data.get('name') or None,
                    algorithm=algorithm,
                    bit_length=bit_length or 2048,
                    mode=data.get('mode') or None,
                    payload_content_type=payload_content_type,
                    expiration=expiration,
                )

            else:
                raise ValueError('Unknown order type: %s' % order_type)

            messages.success(
                request,
                _('Order submitted successfully. Ref: %s') % ref,
            )
            return True
        except Exception as exc:
            exceptions.handle(
                request, _('Unable to submit order: %s') % exc
            )
            return False
