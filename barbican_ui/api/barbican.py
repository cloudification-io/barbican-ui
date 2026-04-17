# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

"""Thin wrapper around python-barbicanclient for Horizon views.

Covers: Secrets, Containers, Orders, Certificates (secret sub-type), ACLs.
"""

import logging

from django.conf import settings

from openstack_dashboard.api import base

from keystoneauth1.identity import v3 as ks_v3
from keystoneauth1 import session as ks_session

from barbicanclient import client as barbican_client

LOG = logging.getLogger(__name__)

BARBICAN_SERVICE_TYPE = 'key-manager'
BARBICAN_UI_USER_AGENT = 'barbican-ui'

# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------

def _barbican_endpoint(request):
    """Return the unversioned Barbican API base URL."""
    endpoint = getattr(settings, 'BARBICAN_ENDPOINT', None)
    endpoint_type = getattr(settings, 'BARBICAN_ENDPOINT_TYPE', 'publicURL')
    try:
        endpoint = endpoint or base.url_for(
            request, 'key-manager', endpoint_type=endpoint_type
        )
    except Exception:
        return None
    endpoint = endpoint.rstrip('/')
    if endpoint.endswith('/v1'):
        endpoint = endpoint[:-3]
    return endpoint


def barbianclient(request):
    """Return a barbicanclient.Client using Horizon's token."""

    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)

    barbican_url = ''
    try:
        barbican_url = base.url_for(request, BARBICAN_SERVICE_TYPE)
    except exceptions_base.ServiceCatalogException:
        LOG.debug('No key-manager service configured in the catalog.')
        return None

    LOG.debug(
        'barbianclient connection created using token "%s" and url "%s"',
        request.user.token.id,
        barbican_url,
    )

    verify = False if insecure else (cacert or True)

    auth = ks_v3.Token(
        auth_url=getattr(settings, 'OPENSTACK_KEYSTONE_URL',
                         'http://localhost:5000/v3'),
        token=request.user.token.id,
        project_id=request.user.tenant_id,
    )
    session = ks_session.Session(auth=auth, verify=verify)

    return barbican_client.Client(
        session=session,
        endpoint=barbican_url,
    )

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ref_to_uuid(ref):
    """Extract the UUID tail from a Barbican href.  Returns '' for falsy."""
    if ref:
        return ref.rstrip('/').split('/')[-1]
    return ''


def build_ref(request, resource, uuid):
    """Build a full Barbican href from resource type and UUID.

    Example::

        build_ref(request, 'secrets', 'abc-123')
        # -> 'https://barbican:9311/v1/secrets/abc-123'
    """
    endpoint = _barbican_endpoint(request)
    if endpoint:
        return '{}/v1/{}/{}'.format(endpoint, resource, uuid)
    return uuid


# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------

def secret_list(request, **kwargs):
    """Return a list of Secret objects for the current project."""
    return list(barbianclient(request).secrets.list(**kwargs))


def secret_get(request, secret_ref):
    """Return a single Secret by its full href."""
    return barbianclient(request).secrets.get(secret_ref)


def secret_create(request, name=None, payload=None,
                  payload_content_type='text/plain',
                  payload_content_encoding=None,
                  algorithm=None, bit_length=None, mode=None,
                  secret_type='opaque', expiration=None):
    """Store a new secret and return its href."""
    c = barbianclient(request)
    s = c.secrets.create(
        name=name,
        payload=payload,
        payload_content_type=payload_content_type if payload else None,
        payload_content_encoding=payload_content_encoding,
        algorithm=algorithm,
        bit_length=bit_length,
        mode=mode,
        secret_type=secret_type,
        expiration=expiration,
    )
    return s.store()


def secret_delete(request, secret_ref):
    """Delete a secret by its full href."""
    barbianclient(request).secrets.delete(secret_ref)


def secret_get_payload(request, secret_ref):
    """Retrieve and return the decrypted payload of a secret."""
    return barbianclient(request).secrets.get(secret_ref).payload


def secret_metadata_get(request, secret_ref):
    """Return the metadata dict for a secret (empty dict if none)."""
    s = barbianclient(request).secrets.get(secret_ref)
    return getattr(s, 'metadata', None) or {}


# ---------------------------------------------------------------------------
# Containers
# ---------------------------------------------------------------------------

def container_list(request, **kwargs):
    """Return a list of Container objects for the current project."""
    return list(barbianclient(request).containers.list(**kwargs))


def container_get(request, container_ref):
    """Return a single Container by its full href."""
    return barbianclient(request).containers.get(container_ref)


def container_create(request, container_type='generic',
                     name=None, secrets=None):
    """Create a container and return its href."""
    c = barbianclient(request)
    secrets = secrets or {}

    if container_type == 'certificate':
        secret_objects = {
            k: c.secrets.get(v) for k, v in secrets.items() if v
        }
        obj = c.containers.create_certificate(name=name, **secret_objects)
    elif container_type == 'rsa':
        secret_objects = {
            k: c.secrets.get(v) for k, v in secrets.items() if v
        }
        obj = c.containers.create_rsa(name=name, **secret_objects)
    else:
        # generic container
        obj = c.containers.create(name=name)
        for label, ref in secrets.items():
            if ref:
                obj.add(label, c.secrets.get(ref))
    return obj.store()


def container_secret_refs(container):
    """Return a list of {'name': str, 'ref': str} dicts from a Container.

    barbicanclient Container.secret_refs is a dict-like mapping of
    {name: SecretRef}.  We normalise it to plain strings for the template.
    """
    refs = []
    try:
        for name, secret_ref in (container.secret_refs or {}).items():
            # secret_ref may be a SecretRef object; coerce to string
            refs.append({
                'name': name,
                'ref': str(getattr(secret_ref, 'secret_ref', secret_ref)),
            })
    except Exception:
        pass
    return refs


def container_delete(request, container_ref):
    """Delete a container by its full href."""
    barbianclient(request).containers.delete(container_ref)


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

def order_list(request, **kwargs):
    """Return a list of Order objects for the current project."""
    return list(barbianclient(request).orders.list(**kwargs))


def order_get(request, order_ref):
    """Return a single Order by its full href."""
    return barbianclient(request).orders.get(order_ref)


def order_create_key(request, **kwargs):
    """Submit a symmetric key generation order and return its href."""
    return barbianclient(request).orders.create_key(**kwargs).submit()


def order_create_asymmetric(request, **kwargs):
    """Submit an asymmetric key pair order and return its href."""
    return barbianclient(request).orders.create_asymmetric(**kwargs).submit()


def order_delete(request, order_ref):
    """Delete an order by its full href."""
    barbianclient(request).orders.delete(order_ref)


# ---------------------------------------------------------------------------
# ACLs
# ---------------------------------------------------------------------------

def acl_get(request, entity_ref):
    """Return current 'read' ACL for entity_ref as a plain dict.

    python-barbicanclient's acls.get() returns an ACLList object.
    The 'read' operation is exposed as acl_list.read (an ACLEntity).

    Returns:
        dict with keys:
            'users'          - list of user UUID strings (may be empty)
            'project_access' - bool (True = all project members can read)
        Defaults to {'users': [], 'project_access': True} on any error
        or when no ACL has been set yet.
    """
    c = barbianclient(request)
    try:
        acl_list = c.acls.get(entity_ref)
        read_acl = getattr(acl_list, 'read', None)
        if read_acl is not None:
            users = list(getattr(read_acl, 'users', None) or [])
            project_access = bool(getattr(read_acl, 'project_access', True))
        else:
            users = []
            project_access = True
    except Exception as exc:
        LOG.warning('acl_get failed for %s: %s', entity_ref, exc)
        users = []
        project_access = True

    return {'users': users, 'project_access': project_access}


def acl_submit(request, entity_ref, users=None,
               project_access=True, operation_type='read'):
    """Set or replace the ACL for a secret or container.

    The python-barbicanclient ACL API works as follows:
      1. acls.get(entity_ref) -> ACLList object
      2. ACLList has per-operation attributes: acl_list.read, acl_list.write
      3. To update, mutate the ACLEntity attributes then call acl_list.submit()
      4. If no ACLEntity exists for the operation yet, call acl_list.add(...)
         before submit().

    :param entity_ref:      Full Barbican href of the secret or container.
    :param users:           List of Keystone user UUID strings.
    :param project_access:  True = all project members can perform operation.
    :param operation_type:  Which operation to set ACL for (default: 'read').
    """
    c = barbianclient(request)
    acl_list = c.acls.get(entity_ref)

    # Check whether an ACLEntity already exists for this operation
    existing = getattr(acl_list, operation_type, None)

    if existing is not None:
        # Mutate in place — barbicanclient tracks dirty state internally
        existing.users = list(users or [])
        existing.project_access = bool(project_access)
    else:
        # No existing ACL for this operation — create one
        acl_list.add(
            operation_type,
            users=list(users or []),
            project_access=bool(project_access),
        )

    # submit() PUTs the full ACL back to Barbican
    return acl_list.submit()


def acl_delete(request, entity_ref):
    """Remove all ACL entries from a secret or container."""
    c = barbianclient(request)
    acl_list = c.acls.get(entity_ref)
    acl_list.remove()
