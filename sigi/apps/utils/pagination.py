from rest_framework.pagination import PageNumberPagination
from rest_framework.settings import api_settings


class SigiPageNumberPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 100
