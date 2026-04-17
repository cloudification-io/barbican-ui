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
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy

from horizon import tables

from barbican_ui.api import barbican

LOG = logging.getLogger(__name__)


class CreateOrder(tables.LinkAction):
    name = 'create'
    verbose_name = _('Create Order')
    url = 'horizon:project:barbican_orders:create'
    classes = ('ajax-modal',)
    icon = 'plus'
    policy_rules = (('key-manager', 'orders:post'),)


class DeleteOrder(tables.DeleteAction):
    help_text = _('Deleted orders cannot be recovered.')
    policy_rules = (('key-manager', 'orders:delete'),)

    @staticmethod
    def action_present(count):
        return ngettext_lazy('Delete Order', 'Delete Orders', count)

    @staticmethod
    def action_past(count):
        return ngettext_lazy('Deleted Order', 'Deleted Orders', count)

    def delete(self, request, obj_id):
        # obj_id is UUID; reconstruct full href
        ref = barbican.build_ref(request, 'orders', obj_id)
        barbican.order_delete(request, ref)


class ViewOrder(tables.LinkAction):
    name = 'detail'
    verbose_name = _('View Details')
    url = 'horizon:project:barbican_orders:detail'
    icon = 'eye'

    def get_link_url(self, order):
        uuid = barbican.ref_to_uuid(order.order_ref)
        return reverse('horizon:project:barbican_orders:detail', args=[uuid])


class OrderFilterAction(tables.FilterAction):
    name = 'filter_orders'
    verbose_name = _('Filter Orders')
    filter_type = 'query'
    filterparam = 'filter_orders'


class OrdersTable(tables.DataTable):

    order_type = tables.Column(
        '_type',
        verbose_name=_('Type'),
        empty_value=_('—'),
    )
    status = tables.Column(
        'status',
        verbose_name=_('Status'),
    )
    secret_ref = tables.Column(
        'secret_ref',
        verbose_name=_('Generated Secret'),
        empty_value=_('—'),
        truncate=60,
    )
    error_status_code = tables.Column(
        'error_status_code',
        verbose_name=_('Error Code'),
        empty_value=_('—'),
    )
    error_reason = tables.Column(
        'error_reason',
        verbose_name=_('Error Reason'),
        empty_value=_('—'),
        truncate=80,
    )
    created = tables.Column(
        'created',
        verbose_name=_('Created'),
    )

    def get_object_id(self, order):
        # Return UUID only
        return barbican.ref_to_uuid(order.order_ref)

    def get_object_display(self, order):
        return '{} ({})'.format(
            getattr(order, '_type', '') or 'order',
            barbican.ref_to_uuid(order.order_ref),
        )

    class Meta:
        name = 'orders'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        table_actions = (CreateOrder, DeleteOrder, OrderFilterAction)
        row_actions = (ViewOrder, DeleteOrder)
