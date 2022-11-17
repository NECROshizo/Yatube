from django.core.paginator import Paginator

from .consts import SHOW_POST

def call_paginator(request, posts, post_in_page=SHOW_POST):
    """Пагинатор"""
    paginator = Paginator(posts, post_in_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
