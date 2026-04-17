# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# barbican-ui local settings override.
#
# Manual installation:
#   cp barbican_ui/local_settings/d/_91_barbican_settings.py \
#      <horizon>/openstack_dashboard/local/local_settings.d/
#
# Some distributions copy plugin settings snippets during packaging. If yours
# does not, copy this file manually as shown above.

# ---- Endpoint -----------------------------------------------------------
# Endpoint type used to look up Barbican in the Keystone service catalog.
# Valid values: publicURL | internalURL | adminURL
BARBICAN_ENDPOINT_TYPE = 'publicURL'

# Hard-code the Barbican API base URL.
# When set this takes precedence over the service catalog lookup.
# Leave commented out to use the catalog (recommended for most deployments).
# BARBICAN_ENDPOINT = 'http://barbican.example.com:9311'

# ---- TLS / SSL ----------------------------------------------------------
# Set to True to disable TLS certificate verification (NOT for production).
BARBICAN_INSECURE = False

# Path to a CA bundle PEM file used when verifying Barbican's TLS cert.
# Set to None to use the system default CA bundle.
BARBICAN_CACERT = None

# ---- UI -----------------------------------------------------------------
# Number of rows shown per page in the Secrets / Containers / Orders tables.
BARBICAN_DEFAULT_PAGE_SIZE = 10
