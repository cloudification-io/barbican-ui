# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

from django.urls import re_path

from barbican_ui.content.orders import views

app_name = 'barbican_orders'

urlpatterns = [
    re_path(r'^orders/$',
            views.IndexView.as_view(),
            name='index'),
    re_path(r'^orders/create/$',
            views.CreateView.as_view(),
            name='create'),
    re_path(r'^orders/(?P<order_id>[^/]+)/$',
            views.DetailView.as_view(),
            name='detail'),
]
