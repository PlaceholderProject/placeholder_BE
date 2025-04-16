# -*- coding: utf-8 -*-
from typing import Any, List
from urllib.parse import urlencode, urlparse, urlunparse

from ninja import Schema
from ninja.pagination import PaginationBase


class CustomPagination(PaginationBase):
    items_attribute: str = "result"

    class Input(Schema):
        page: int | None = 1
        size: int | None = 10

    class Output(Schema):
        result: List[Any]
        total: int
        previous: str | None = None
        next: str | None = None

    def paginate_queryset(self, queryset, pagination: Input, **params):
        page = pagination.page
        size = pagination.size
        request = params["request"]
        offset = (page - 1) * size
        total = queryset.count()

        def build_url(new_page):
            if new_page < 1 or new_page > ((total - 1) // size) + 1:
                return None

            query_params = request.GET.copy()
            query_params["page"] = new_page
            query_params["size"] = size

            url_parts = list(urlparse(request.build_absolute_uri()))
            url_parts[4] = urlencode(query_params, doseq=True)
            return urlunparse(url_parts)

        previous_url = build_url(page - 1) if page > 1 else None
        next_url = build_url(page + 1) if offset + size < total else None
        return {
            "result": queryset[offset : offset + size],  # noqa: E203
            "total": total,
            "previous": previous_url,
            "next": next_url,
        }
