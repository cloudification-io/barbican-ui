# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

"""Minimal Django settings for running barbican-ui unit tests.

Mirrors the pattern used by manila-ui and other Horizon plugin test suites.
Horizon's own test settings are imported as a base so all the required
middleware, template loaders and context processors are present without
duplicating them here.
"""

import barbican_ui
import os

# ---------------------------------------------------------------------------
# Import Horizon's test settings as a base
# ---------------------------------------------------------------------------
try:
    from openstack_dashboard.test.settings import *  # noqa: F401,F403
except ImportError:
    # Fallback minimal settings when horizon is not installed in the venv yet
    # (e.g. first `pip install -r requirements.txt` run).
    pass

# ---------------------------------------------------------------------------
# Override / extend for barbican-ui
# ---------------------------------------------------------------------------

# Make sure barbican_ui is in INSTALLED_APPS so Django finds its templates.
INSTALLED_APPS = list(globals().get('INSTALLED_APPS', [])) + [
    'barbican_ui',
]

_BARBICAN_UI_DIR = os.path.dirname(os.path.dirname(
    os.path.abspath(barbican_ui.__file__)
))

# Horizon test settings already configure TEMPLATES; we just need to ensure
# barbican_ui/templates is on the path.
_TEMPLATES = globals().get('TEMPLATES', [])
if _TEMPLATES:
    for _t in _TEMPLATES:
        _dirs = _t.get('DIRS', [])
        _barbican_tmpl = os.path.join(
            _BARBICAN_UI_DIR, 'barbican_ui', 'templates'
        )
        if _barbican_tmpl not in _dirs:
            _dirs.append(_barbican_tmpl)
        _t['DIRS'] = _dirs
else:
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(
                    _BARBICAN_UI_DIR, 'barbican_ui', 'templates'
                ),
            ],
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
                'loaders': [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ],
            },
        }
    ]

# Test-only: point to a simple SQLite DB so Django doesn't complain.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Silence deprecation warnings in tests.
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Barbican-specific settings used by the API wrapper in tests.
BARBICAN_ENDPOINT = 'http://barbican.example.com:9311'
BARBICAN_ENDPOINT_TYPE = 'publicURL'
BARBICAN_INSECURE = False
BARBICAN_CACERT = None
BARBICAN_DEFAULT_PAGE_SIZE = 10

# Disable CSRF for test client calls.
MIDDLEWARE = [
    m for m in globals().get('MIDDLEWARE', [])
    if 'csrf' not in m.lower()
] or [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Root URL conf used by the test client.
ROOT_URLCONF = globals().get('ROOT_URLCONF', 'openstack_dashboard.urls')

# Silence noisy loggers during tests.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {'class': 'logging.NullHandler'},
    },
    'loggers': {
        'barbican_ui': {'handlers': ['null'], 'propagate': False},
        'openstack_dashboard': {'handlers': ['null'], 'propagate': False},
        'horizon': {'handlers': ['null'], 'propagate': False},
        'keystoneauth1': {'handlers': ['null'], 'propagate': False},
        'barbicanclient': {'handlers': ['null'], 'propagate': False},
    },
}

# Keystone URL used by the barbican API wrapper.
OPENSTACK_KEYSTONE_URL = 'http://keystone.example.com:5000/v3'
