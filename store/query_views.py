from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, connection
from django.db.models import Q, F
from django.db.models import Value, Func, ExpressionWrapper, DecimalField
from django.db.models.aggregates import Count, Min, Max, Avg
from django.shortcuts import render
from tags.models import TaggedItem

from .models import Collection, Order, Product, OrderItem
from .models import Customer


def query_database(request):
    name = "Jhon"

    # list all products
    query_set = Product.objects.all()

    try:
        product = Product.objects.get(pk=1)
    except ObjectDoesNotExist:
        pass

    # get a customer with primary key 1
    customer = Customer.objects.filter(pk=1).first()

    # check if a customer exists
    exists = Customer.objects.filter(pk=100).exists()

    # products which unit_price is greater than 20
    products_unit_price__gt_20 = Product.objects.filter(unit_price__gt=20)

    # products which unit_price is in range 20 to 30
    products_unit_price__range_20_30 = Product.objects.filter(
        unit_price__range=(20, 30))

    # products which collection id is in range 1 to 5
    products_collection_id__range_1_5 = Product.objects.filter(
        collection__id__range=(1, 5))

    # products which title contains "coffee"
    products_title__icontains_coffee = Product.objects.filter(
        title__icontains="coffee")

    # products which title starts with "co"
    products_title__istartswith_co = Product.objects.filter(
        title__istartswith="co")

    # products which last_update year is 2021
    products_last_update__year_2021 = Product.objects.filter(
        last_update__year=2021)

    # products which description is null
    products_description__isnull = Product.objects.filter(
        description__isnull=True)

    # products which inventory is less than 10 and unit_price is greater than 20
    products_inventory__lt_10_and_unit_price__gt_20 = Product.objects.filter(
        inventory__lt=10, unit_price__gt=20)

    # products which inventory is less than or equal 10 and unit_price is greater than or equal 20
    products_inventory__lte_10_and_unit_price__gte_20 = Product.objects.filter(
        inventory__lte=10).filter(unit_price__gte=20)

    # products which inventory is greater than or equal 10 or unit_price is greater less or equal 20
    products_inventory__gte_10_or_unit_price__lt_20 = Product.objects.filter(
        Q(inventory__lt=10) | (Q(unit_price__lt=20)))

    # products which inventory is equal to unit_price
    products_inventory_F_unit_price = Product.objects.filter(
        inventory=F("unit_price"))

    # products which inventory is equal to collection id
    products_inventory_F_collection__id = Product.objects.filter(
        inventory=F("collection__id"))

    # products which title is in ascending order
    products_title_ascending = Product.objects.all().order_by("title")

    # products which title is in descending order
    products_title_descending = Product.objects.all().order_by("-title")

    # products which unit_price is in ascending order and title is in descending
    products_unit_price_ascending_and_title_descending = Product.objects.all().order_by(
        "unit_price", "-title")

    # products which unit_price is in reverse ascending order and title is in reverse descending order
    products_unit_price_ascending_and_title_descending_reverse = Product.objects.all().order_by(
        "unit_price", "-title").reverse()

    # products which unit_price is earliest
    product_unit_price_earliest = Product.objects.earliest("unit_price")

    # products which unit_price is latest
    product_unit_price_latest = Product.objects.latest("unit_price")

    # get 5 products from index 0 to 4
    products_limit_5 = Product.objects.all()[:5]

    # get 5 products from index 5 to 9
    products_limit_5_offset_5 = Product.objects.all()[5:10]

    # returns dictionaries of products with column title, unit_price and collection title
    products_title_unit_price_collection__title_values = Product.objects.values(
        "title", "unit_price", "collection__title")

    # returns tuples of products with column title, unit_price and collection title
    products_title_unit_price_collection__values_list = Product.objects.values_list(
        "title", "unit_price", "collection__title")

    # get distinct ids of order items, returns dictionaries
    order_item_ids = OrderItem.objects.values("product__id").distinct()

    # get products which are in order items
    order_item_products_title_ascending = Product.objects.filter(
        id__in=order_item_ids).order_by("title")

    # get column title, description and unit_price of products
    products_title_description_only = Product.objects.only(
        "title", "description", "unit_price")

    # get all columns except description, inventory, last_update and slug of products
    products_description_inventory_last_update_slug_defer = Product.objects.defer(
        "description", "inventory", "last_update", "slug")

    # preload collection table when fetching products
    products_title_unit_price_collection = Product.objects.select_related(
        "collection").all()

    # preload promotion table when fetching products
    products_title_unit_price_promotions = Product.objects.prefetch_related(
        "promotions").all()

    # preload collection and promotion table when fetching products
    products_title_unit_price_promotions_collection = Product.objects.prefetch_related(
        "promotions").select_related("collection").all()

    # get top 5 customers with products order by placed_at in reverse ooder
    orders_customer_order_items_products_top_5 = Order.objects.select_related(
        "customer").prefetch_related("orderitem_set__product").order_by("-placed_at")[:5]

    # get count, minimum price, maximum price and average price of products
    result = Product.objects.aggregate(count=Count("id"), min_price=Min(
        "unit_price"), max_price=Max("unit_price"), avg_price=Avg("unit_price"))

    # returns customers with new field is_new
    customers_annotate_is_new = Customer.objects.annotate(is_new=Value(True))

    # returns customers with new field new_id
    customers_annotate_new_id = Customer.objects.annotate(new_id=F("id"))

    # returns customers with new field full_name
    customers_annotate_full_name = Customer.objects.annotate(
        full_name=Func(F("first_name"), Value(
            " "), F("last_name"), function="CONCAT")
    )

    # returns customers with new field containing orders count
    customers_annotate_orders_count = Customer.objects.annotate(
        orders_count=Count("order"))

    # returns products with new calculated field discounted_price
    discounted_price = ExpressionWrapper(
        F("unit_price") * 0.8, output_field=DecimalField())
    products_annotate_discount = Product.objects.annotate(
        discounted_price=discounted_price)

    # get tags of product id 1
    content_type = ContentType.objects.get_for_model(Product)
    tagged_items = TaggedItem.objects.select_related(
        "tag").filter(content_type=content_type, object_id=1)

    # get tags of product id 1 using custom method "get_tags_for"
    tagged_items_custom_manager = TaggedItem.objects.get_tags_for(Product, 1)

    return render(request, "index.html", {
        "name": name,
        "products_list": list(order_item_products_title_ascending),
        "product": product_unit_price_latest,
        "products": products_title_unit_price_promotions_collection,
        "products_objects_only": products_title_description_only,
        "products_objects_defer": products_description_inventory_last_update_slug_defer,
        "orders": orders_customer_order_items_products_top_5,
        "result": result,
        "queryset": list(tagged_items_custom_manager),
    })


def create_object(request):
    collection = Collection()
    collection.title = "Video Games"
    collection.featured_product = Product(pk=1)
    collection.save()
    return render(request, "index.html", {
        "name": collection
    })


def update_object(request):
    collection = Collection.objects.get(pk=11)
    collection.featured_product = None
    collection.save()

    return render(request, "index.html", {
        "name": collection
    })


def delete_object(request):
    collection = Collection(pk=11)
    collection.delete()

    Collection.objects.filter(id__gte=10).delete()

    return render(request, "index.html")


def transaction_object(request):
    with transaction.atomic():
        order = Order()
        order.customer = Customer(pk=1)
        order.payment_status = "P"
        order.save()

        order_item = OrderItem()
        order_item.order = order
        order_item.product = Product(pk=1)
        order_item.quantity = 1
        order_item.unit_price = 10
        order_item.save()

    return render(request, "index.html")


def raw_sql(request):
    products = Product.objects.raw("SELECT * FROM store_product")

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM store_customer")
        customers = cursor.fetchall()

    return render(request, "index.html", {
        "products_list": products,
        "customers_list": customers
    })
