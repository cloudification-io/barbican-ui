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
from barbican_ui.content.containers import views

app_name = 'barbican_containers'

urlpatterns = [
    re_path(r'^containers/$',
            views.IndexView.as_view(),
            name='index'),
    re_path(r'^containers/create/$',
            views.CreateView.as_view(),
            name='create'),
    re_path(r'^containers/(?P<container_id>[^/]+)/$',
            views.DetailView.as_view(),
            name='detail'),
    # ACL management is nested under containers so that
    # reverse('horizon:project:barbican_containers:acl') resolves correctly.
    re_path(r'^containers/(?P<container_id>[^/]+)/acl/$',
            acl_views.ManageContainerACLView.as_view(),
            name='acl'),
]
