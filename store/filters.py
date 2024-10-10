from django_filters.rest_framework import FilterSet

from . import models


class ProductFilter(FilterSet):
    class Meta:
        model = models.Product
        fields = {
            "collection_id": ["exact"],
            "unit_price": ["gt", "lt"]
        }


class CustomerFilter(FilterSet):
    class Meta:
        model = models.Customer
        fields = {
            # "first_name": ["iexact"],
            # "last_name": ["iexact"],
            # "email": ["iexact"],
            "phone": ["iexact"]
        }
