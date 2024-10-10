from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .signals import order_created
from . import models


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductImage
        fields = ["id", "image"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        return models.ProductImage.objects.create(product_id=product_id, **validated_data)


class ProductSerializer(serializers.ModelSerializer):
    productimage_set = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = models.Product
        fields = ["id", "title", "slug", "description", "unit_price",
                  "price_with_tax", "inventory", "collection", "orders", "collection_title", "last_update", "productimage_set"]

    collection_title = serializers.SerializerMethodField(
        method_name="get_collection_title")

    price_with_tax = serializers.SerializerMethodField(
        method_name="calculate_tax")

    orders = serializers.SerializerMethodField(
        method_name="calculate_orders_count")

    """
    collection = serializers.HyperlinkedRelatedField(
        queryset=models.Collection.objects.all(),
        view_name="collection-detail"
    )
    """

    def get_collection_title(self, product: models.Product):
        return product.collection.title

    def calculate_orders_count(self, product: models.Product):
        return product.orderitem_set.count()

    def calculate_tax(self, product: models.Product):
        return product.unit_price * Decimal(1.5)


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ["id", "title", "products_count"]

    """
    products_count = serializers.SerializerMethodField(
        method_name="get_products_count")
    """

    products_count = serializers.IntegerField(read_only=True)

    """
    def get_products_count(self, collection: models.Collection):
        return collection.product_set.count()
    """


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ["id", "name", "description", "date"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        return models.Review.objects.create(product_id=product_id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ["id", "title", "unit_price"]


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(
        method_name="get_total_price")

    def get_total_price(self, cartitem: models.CartItem):
        return cartitem.product.unit_price * cartitem.quantity

    class Meta:
        model = models.CartItem
        fields = ["id", "product", "quantity", "total_price"]


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not models.Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                "Product with the given id does not exists.")
        return value

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]
        try:
            cart_item = models.CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except models.CartItem.DoesNotExist:
            self.instance = models.CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = models.CartItem
        fields = ["id", "product_id", "quantity"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ["quantity"]


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    cartitem_set = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(
        method_name="get_total_price")

    def get_total_price(self, cart: models.Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.cartitem_set.all()])

    class Meta:
        model = models.Cart
        fields = ["id", "cartitem_set", "total_price"]


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Customer
        fields = ["id", "user_id", "phone", "birth_date", "membership"]

    """
    full_name = serializers.SerializerMethodField(method_name="get_full_name")

    def get_full_name(self, customer: models.Customer):
        return f"{customer.first_name} {customer.last_name}"
    """


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = models.OrderItem
        fields = ["id", "product", "quantity", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    orderitem_set = OrderItemSerializer(many=True)
    payment_status = serializers.ReadOnlyField()

    class Meta:
        model = models.Order
        fields = ["id", "customer_id", "placed_at",
                  "payment_status", "orderitem_set"]


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not models.Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                "No cart with the given ID was found.")
        if models.CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError("The cart is empty.")
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            user_id = self.context["user_id"]
            cart_id = self.validated_data["cart_id"]

            # getting the customer by user_id
            customer = models.Customer.objects.get(user_id=user_id)

            # creating order with the above customer
            order = models.Order.objects.create(customer=customer)

            # getting cart items by cart_id
            cart_items = models.CartItem.objects.select_related(
                "product").filter(cart_id=cart_id)

            # creating order items to save in database
            order_items = [
                models.OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]

            # saving cart items to database
            models.OrderItem.objects.bulk_create(order_items)

            # deleting existing cart
            models.Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(self.__class__, order=order)

            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ["payment_status"]
