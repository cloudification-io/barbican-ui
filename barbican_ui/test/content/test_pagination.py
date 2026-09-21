# Copyright 2026 Cloudification GmbH
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0

from unittest import mock

from django.test import RequestFactory
import pytest

from barbican_ui.content.certificates import views as certificate_views
from barbican_ui.content import pagination
from barbican_ui.content.secrets import tables as secret_tables
from barbican_ui.content.secrets import views as secret_views


def _view(view_class, query=''):
    view = view_class()
    view.request = RequestFactory().get('/' + query)
    return view


def _rows(count):
    return [mock.Mock(secret_ref='ref-%d' % i) for i in range(count)]


def test_first_page_asks_for_one_extra_row(settings):
    settings.BARBICAN_DEFAULT_PAGE_SIZE = 3
    view = _view(secret_views.IndexView)

    with mock.patch.object(secret_views.barbican, 'secret_list',
                           return_value=_rows(4)) as secret_list:
        data = view.get_data()

    secret_list.assert_called_once_with(view.request, limit=4, offset=0)
    assert len(data) == 3
    assert view.has_more_data(None) is True
    assert view.has_prev_data(None) is False


@pytest.mark.parametrize('query', ['?marker=3', '?prev_marker=3'])
def test_last_page_has_only_a_previous_link(settings, query):
    settings.BARBICAN_DEFAULT_PAGE_SIZE = 3
    view = _view(secret_views.IndexView, query)

    with mock.patch.object(secret_views.barbican, 'secret_list',
                           return_value=_rows(2)) as secret_list:
        data = view.get_data()

    secret_list.assert_called_once_with(view.request, limit=4, offset=3)
    assert len(data) == 2
    assert view.has_more_data(None) is False
    assert view.has_prev_data(None) is True


@pytest.mark.parametrize('query', ['?marker=abc', '?marker=-5'])
def test_a_bad_marker_falls_back_to_the_first_page(settings, query):
    settings.BARBICAN_DEFAULT_PAGE_SIZE = 3
    view = _view(secret_views.IndexView, query)

    with mock.patch.object(secret_views.barbican, 'secret_list',
                           return_value=[]) as secret_list:
        view.get_data()

    assert secret_list.call_args.kwargs['offset'] == 0


@pytest.mark.parametrize('query,marker,prev_marker', [
    ('', '3', '0'),
    ('?marker=3', '6', '0'),
    ('?marker=6', '9', '3'),
])
def test_table_markers_are_offsets(settings, query, marker, prev_marker):
    settings.BARBICAN_DEFAULT_PAGE_SIZE = 3
    table = secret_tables.SecretsTable(RequestFactory().get('/' + query),
                                       data=_rows(3))

    assert table.get_marker() == marker
    assert table.get_prev_marker() == prev_marker


@pytest.mark.parametrize('configured,size', [
    (None, 10), (25, 25), (500, 99), (0, 10),
])
def test_page_size_stays_within_the_barbican_limit(settings, configured,
                                                   size):
    settings.BARBICAN_DEFAULT_PAGE_SIZE = configured

    assert pagination.page_size() == size


def test_certificates_are_filtered_by_barbican(settings):
    settings.BARBICAN_DEFAULT_PAGE_SIZE = 3
    view = _view(certificate_views.IndexView)

    with mock.patch.object(certificate_views.barbican, 'secret_list',
                           return_value=[]) as secret_list:
        view.get_data()

    secret_list.assert_called_once_with(
        view.request, limit=4, offset=0, secret_type='certificate')


def _pages(pages):
    def secret_list(request, limit, offset):
        return _rows(pages.get(offset, 0))
    return secret_list


def test_an_empty_page_shows_the_previous_page(settings):
    settings.BARBICAN_DEFAULT_PAGE_SIZE = 3
    view = _view(secret_views.IndexView, '?marker=6')

    with mock.patch.object(secret_views.barbican, 'secret_list',
                           side_effect=_pages({3: 3})) as secret_list:
        data = view.get_data()

    assert [c.kwargs['offset'] for c in secret_list.call_args_list] == [6, 3]
    assert len(data) == 3
    assert view.has_prev_data(None) is True
    table = secret_tables.SecretsTable(view.request, data=data)
    assert (table.get_prev_marker(), table.get_marker()) == ('0', '6')


def test_a_marker_far_past_the_end_shows_the_first_page(settings):
    settings.BARBICAN_DEFAULT_PAGE_SIZE = 3
    view = _view(secret_views.IndexView, '?marker=300')

    with mock.patch.object(secret_views.barbican, 'secret_list',
                           side_effect=_pages({0: 2})) as secret_list:
        data = view.get_data()

    assert [c.kwargs['offset'] for c in secret_list.call_args_list] == [
        300, 297, 0]
    assert len(data) == 2
    assert view.has_prev_data(None) is False


def test_an_empty_first_page_is_not_retried(settings):
    settings.BARBICAN_DEFAULT_PAGE_SIZE = 3
    view = _view(secret_views.IndexView)

    with mock.patch.object(secret_views.barbican, 'secret_list',
                           side_effect=_pages({})) as secret_list:
        assert view.get_data() == []

    assert secret_list.call_count == 1
