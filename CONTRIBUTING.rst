============
Contributing
============

barbican-ui follows the standard OpenStack contribution workflow.

* Source:  https://opendev.org/openstack/barbican-ui
* Reviews: https://review.opendev.org/q/project:openstack/barbican-ui
* Bugs:    https://bugs.launchpad.net/barbican-ui
* IRC:     ``#openstack-barbican`` on OFTC

How to Contribute
-----------------

1. Create a Launchpad account and sign the CLA:
   https://wiki.openstack.org/wiki/How_To_Contribute

2. Clone the repo and set up Gerrit::

       git clone https://opendev.org/openstack/barbican-ui
       cd barbican-ui
       git review -s

3. Create a topic branch::

       git checkout -b my-feature

4. Make your changes, write tests, and run the test suite::

       tox -e py311
       tox -e pep8

5. Commit and push for review::

       git commit -am "My descriptive commit message"
       git review

Coding Standards
----------------

* Follow OpenStack Hacking guidelines (``tox -e pep8``).
* Every new behaviour must be covered by a unit test.
* Tests live under ``barbican_ui/test/``, mirroring the source tree.
* Use ``gettext_lazy`` (``_(...)``) for all user-visible strings.
