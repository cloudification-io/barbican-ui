# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

from django.urls import re_path

from barbican_ui.content.acls import views as acl_views
from barbican_ui.content.secrets import views

app_name = 'barbican_secrets'

urlpatterns = [
    re_path(r'^secrets/$',
            views.IndexView.as_view(),
            name='index'),
    re_path(r'^secrets/create/$',
            views.CreateView.as_view(),
            name='create'),
    re_path(r'^secrets/(?P<secret_id>[^/]+)/$',
            views.DetailView.as_view(),
            name='detail'),
    re_path(r'^secrets/(?P<secret_id>[^/]+)/reveal/$',
            views.RevealView.as_view(),
            name='reveal'),
    # ACL management is nested under secrets so that
    # reverse('horizon:project:barbican_secrets:acl') resolves correctly.
    # No separate barbican_acls namespace is needed.
    re_path(r'^secrets/(?P<secret_id>[^/]+)/acl/$',
            acl_views.ManageSecretACLView.as_view(),
            name='acl'),
]
