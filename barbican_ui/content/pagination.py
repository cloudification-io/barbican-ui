# Copyright 2026 Cloudification GmbH
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Offset paging for Horizon tables backed by Barbican's limit/offset lists."""

from django.conf import settings

# Barbican's default max_limit_paging is 100; an extra row detects a next page.
MAX_PAGE_SIZE = 99


def page_size():
    size = getattr(settings, 'BARBICAN_DEFAULT_PAGE_SIZE', None) or 10
    return min(max(int(size), 1), MAX_PAGE_SIZE)


def _offset(request, meta):
    effective = getattr(request, '_barbican_ui_offset', None)
    if effective is not None:
        return effective
    raw = (request.GET.get(meta.prev_pagination_param) or
           request.GET.get(meta.pagination_param))
    try:
        return max(int(raw), 0)
    except (TypeError, ValueError):
        return 0


class OffsetPagedTable(object):
    """DataTable mixin whose markers are list offsets, not object ids."""

    def get_marker(self):
        return str(_offset(self.request, self._meta) + page_size())

    def get_prev_marker(self):
        return str(max(_offset(self.request, self._meta) - page_size(), 0))


class OffsetPagedView(object):
    """DataTableView mixin that fetches one page per request."""

    _has_more_data = False
    _has_prev_data = False

    def paginate(self, list_func, **filters):
        size = page_size()
        offset = _offset(self.request, self.table_class._meta)
        items = list_func(self.request, limit=size + 1, offset=offset,
                          **filters)
        # Horizon renders no paging links on an empty page.
        for fallback in (max(offset - size, 0), 0):
            if items or offset == 0:
                break
            offset = fallback
            items = list_func(self.request, limit=size + 1, offset=offset,
                              **filters)
        self.request._barbican_ui_offset = offset
        self._has_more_data = len(items) > size
        self._has_prev_data = offset > 0
        return items[:size]

    def has_more_data(self, table):
        return self._has_more_data

    def has_prev_data(self, table):
        return self._has_prev_data
