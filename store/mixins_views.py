from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from .models import Collection, Product
from .models import Customer
from .serializers import CustomerSerializer, ProductSerializer, CollectionSerializer


class ProductList(ListCreateAPIView):
    queryset = Product.objects.select_related(
        "collection").prefetch_related("orderitem_set").all()

    """    
    def get_queryset(self):
        return Product.objects.select_related("collection").prefetch_related("orderitem_set").all()
    """

    serializer_class = ProductSerializer

    """
    def get_serializer_class(self):
        return ProductSerializer
    """

    def get_serializer_context(self):
        return {"request": self.request}


"""
    def get(self, request):
        queryset = Product.objects.select_related(
            "collection").prefetch_related("orderitem_set").all()

        serializer = ProductSerializer(
            queryset, many=True, context={"request": request})

        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
"""


class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    """    
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)

        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    """

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        if product.orderitem_set.count() > 0:
            return Response({
                "error", "Product can not be deleted because it is associated with an order item."
            },
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        product.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerList(ListCreateAPIView):
    def get_queryset(self):
        return Customer.objects.all()

    def get_serializer_class(self):
        return CustomerSerializer

    """        
    def get(self, request):
        queryset = Customer.objects.all()
        serializer = CustomerSerializer(queryset, many=True)

        return Response(serializer.data)
    """


class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(products_count=Count("product"))
    serializer_class = CollectionSerializer
    """    
    def get(self, request, pk):
        collection = get_object_or_404(Collection.objects.filter(
            pk=pk).annotate(products_count=Count("product")), pk=pk)

        serializer = CollectionSerializer(collection)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        collection = get_object_or_404(Collection.objects.filter(
            pk=pk).annotate(products_count=Count("product")), pk=pk)

        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    """

    def delete(self, request, pk):
        collection = get_object_or_404(Collection.objects.filter(
            pk=pk).annotate(products_count=Count("product")), pk=pk)

        if collection.product_set.count() > 0:
            return Response({
                "error": "Collection can not be deleted because it includes one or more products."
            },
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        collection.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(products_count=Count("product"))
    """
    def get_queryset(self):
        return Collection.objects.annotate(products_count=Count("product"))
    """

    serializer_class = CollectionSerializer
    """
    def get_serializer_class(self):
        return CollectionSerializer
    """

    """
    def get(self, request):
        queryset = Collection.objects.annotate(products_count=Count("product"))
        serializer = CollectionSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    """
