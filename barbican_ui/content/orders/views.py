# Copyright 2024 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

import logging

from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms as horizon_forms
from horizon import tables as horizon_tables
from horizon import views

from barbican_ui.api import barbican
from barbican_ui.content.orders import forms
from barbican_ui.content.orders import tables

LOG = logging.getLogger(__name__)


class IndexView(horizon_tables.DataTableView):
    table_class = tables.OrdersTable
    template_name = 'barbican_ui/orders/index.html'
    page_title = _('Orders')

    def get_data(self):
        try:
            return barbican.order_list(self.request)
        except Exception:
            exceptions.handle(self.request, _('Unable to retrieve orders.'))
            return []


class DetailView(views.HorizonTemplateView):
    """Read-only detail page for a single order (no sub-tables needed)."""

    template_name = 'barbican_ui/orders/detail.html'
    page_title = _('Order Details')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self._get_order()
        context['order'] = order
        context['order_type'] = getattr(order, '_type', None)
        context['url'] = reverse('horizon:project:barbican_orders:index')
        if order:
            # Use order type + short UUID as the page title
            otype = getattr(order, '_type', '') or 'order'
            full_id = barbican.ref_to_uuid(order.order_ref)
            context['page_title'] = '{} ({})'.format(
                otype.capitalize(), full_id
            )
        return context

    def _get_order(self):
        if not hasattr(self, '_order'):
            ref = barbican.build_ref(
                self.request, 'orders', self.kwargs['order_id']
            )
            try:
                self._order = barbican.order_get(self.request, ref)
            except Exception:
                exceptions.handle(
                    self.request,
                    _('Unable to retrieve order details.'),
                    redirect=reverse('horizon:project:barbican_orders:index'),
                )
                self._order = None
        return self._order


class CreateView(horizon_forms.ModalFormView):
    form_class = forms.CreateOrderForm
    form_id = 'create_order_form'
    modal_header = _('Create Order')
    submit_label = _('Submit Order')
    submit_url = reverse_lazy('horizon:project:barbican_orders:create')
    template_name = 'barbican_ui/orders/create.html'
    ajax_template_name = 'barbican_ui/orders/_create.html'
    page_title = _('Create Order')
    success_url = reverse_lazy('horizon:project:barbican_orders:index')
