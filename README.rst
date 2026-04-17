============
barbican-ui
============

OpenStack Key Manager (Barbican) UI panel for OpenStack Horizon.

This plugin provides a modern, Horizon-integrated dashboard for managing
Barbican resources. It replaces the original AngularJS-based barbican-ui
(unmaintained since 2017, incompatible with current Horizon).

* Free software: Apache license
* Source: https://opendev.org/openstack/barbican-ui
* Bugs: https://bugs.launchpad.net/barbican-ui

Panels
------

All panels appear under **Project → Key Manager** in the Horizon sidebar:

* **Secrets** — list, create, delete, reveal payload, view metadata, manage ACL
* **Containers** — list, create, delete, view associated secrets, manage ACL
* **Orders** — submit symmetric-key / asymmetric-key / certificate orders
* **Certificates** — store PEM certificates, download

Requirements
------------

* Python ≥ 3.9
* OpenStack Horizon ≥ 22.0 (Zed or later)
* python-barbicanclient ≥ 5.0.1
* keystoneauth1 ≥ 3.4.0

Installation
------------

**From PyPI:**

.. code-block:: bash

    pip install barbican-ui

When installed via pip the ``openstack_dashboard.enabled`` entry points in
``setup.cfg`` register the panels automatically — no manual file copying
is needed.

**From source:**

.. code-block:: bash

    git clone https://opendev.org/openstack/barbican-ui
    cd barbican-ui
    pip install -e .

**Manual panel registration (no pip):**

Copy the four enabled files into your Horizon installation **in order**
(the ``_91_`` file creates the panel group; the others add panels to it):

.. code-block:: bash

    ENABLED=<horizon>/openstack_dashboard/local/enabled

    cp barbican_ui/enabled/_91*      $ENABLED/

    cp barbican_ui/local_settings/d/_91_barbican_settings.py \
       <horizon>/openstack_dashboard/local/local_settings.d/

**Restart Horizon:**

.. code-block:: bash

    python manage.py collectstatic --noinput
    python manage.py compress --force
    systemctl restart apache2   # or your WSGI server

How the enabled files work
--------------------------

Horizon loads every ``*.py`` file from ``local/enabled/`` in filename
(lexicographic) order at startup. ``barbican_ui/enabled/_91_barbican.py``
will create group. Each file registers exactly one panel:

=========================================================================  ================  =============
File                                                                       Panel             Creates Group?
=========================================================================  ================  =============
``_9110_barbican_project_add_secrets_to_key_manager_panel_group.py``       Secrets           No 
``_9120_barbican_project_add_certificates_to_key_manager_panel_group.py``  Containers        No
``_9130_barbican_project_add_containers_to_key_manager_panel_group.py``    Orders            No
``_9140_barbican_project_add_orders_to_key_manager_panel_group.py``        Certificates      No
=========================================================================  ================  =============

The ``_91_`` file also declares ``ADD_INSTALLED_APPS`` and
``AUTO_DISCOVER_STATIC_FILES`` — the remaining files are intentionally
minimal (just ``PANEL``, ``PANEL_DASHBOARD``, ``PANEL_GROUP``,
``ADD_PANEL``).

Configuration
-------------

Edit ``local_settings.d/_91_barbican_settings.py``:

.. code-block:: python

    # Override endpoint (skips catalog lookup when set)
    # BARBICAN_ENDPOINT = 'http://barbican.example.com:9311'

    BARBICAN_ENDPOINT_TYPE = 'publicURL'   # or 'internalURL'
    BARBICAN_INSECURE = False
    BARBICAN_CACERT = None                 # path to CA bundle PEM, or None
    BARBICAN_DEFAULT_PAGE_SIZE = 10

Running Tests
-------------

.. code-block:: bash

    # All tests via tox
    tox -e py311

    # Directly with Django test runner
    python manage.py test barbican_ui.test \
        --settings=barbican_ui.test.settings

    # PEP-8 / style checks
    tox -e pep8

    # Coverage report
    tox -e cover

DevStack
--------

Add to ``local.conf``:

.. code-block:: ini

    enable_plugin barbican-ui https://opendev.org/openstack/barbican-ui master
    enable_service barbican-ui

Contributing
------------

See ``CONTRIBUTING.rst``.
