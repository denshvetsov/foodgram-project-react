from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """
    Cтандарный пагинатор с переопределенным параметром овечющим
    за максимальный вывод страниц, пример использования
    http://127.0.0.1:8000/api/users/subscriptions/?limit=6
    необходим для совместимости с текущей реализацией api fronend
    """
    page_size_query_param = 'limit'
