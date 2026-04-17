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


class StoreCertificateForm(forms.SelfHandlingForm):
    """Store a PEM-encoded X.509 certificate as a Barbican secret."""

    name = forms.CharField(
        label=_('Name'),
        required=False,
        max_length=255,
        help_text=_('Optional human-readable label.'),
    )
    certificate_pem = forms.CharField(
        label=_('Certificate (PEM)'),
        required=True,
        widget=forms.widgets.Textarea(attrs={'rows': 10}),
        help_text=_(
            'Paste the full PEM block including '
            '-----BEGIN CERTIFICATE----- / -----END CERTIFICATE----- markers.'
        ),
    )
    expiration = forms.CharField(
        label=_('Expiration (UTC)'),
        required=False,
        max_length=32,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DDTHH:MM:SS'}),
        help_text=_('Leave blank for no expiration.'),
    )

    def clean_certificate_pem(self):
        pem = (self.cleaned_data.get('certificate_pem') or '').strip()
        if not pem.startswith('-----BEGIN'):
            raise forms.ValidationError(
                _('Certificate must be in PEM format '
                  '(starts with -----BEGIN CERTIFICATE-----).')
            )
        return pem

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

    def handle(self, request, data):
        try:
            ref = barbican.secret_create(
                request,
                name=data.get('name') or None,
                payload=data['certificate_pem'],
                payload_content_type='application/pkix-cert',
                secret_type='certificate',
                expiration=data.get('expiration'),
            )
            label = data.get('name') or barbican.ref_to_uuid(ref)
            messages.success(
                request,
                _('Certificate "%s" stored successfully.') % label,
            )
            return True
        except Exception as exc:
            exceptions.handle(
                request, _('Unable to store certificate: %s') % exc
            )
            return False
