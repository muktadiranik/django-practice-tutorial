from urllib.parse import urlencode

from django.contrib import admin, messages
from django.db.models import Count, Sum
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.html import format_html

from . import models


# Register your models here.


class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [
            ("<10", "Low")
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['title']
    }
    autocomplete_fields = ["collection"]
    actions = ["clear_inventory"]
    list_display = ['title', 'unit_price', "inventory_status",
                    "last_update", "collection_title"]
    list_display_links = ['title']
    list_editable = ["unit_price"]
    list_filter = ["collection", "last_update", InventoryFilter]
    list_per_page = 10
    list_select_related = ["collection"]
    search_fields = ["title"]

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        if product.inventory < 10:
            return "Low"
        return "OK"

    def collection_title(self, product):
        return product.collection.title

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset: QuerySet):
        updated_count = queryset.update(inventory=1)
        self.message_user(
            request,
            f"{updated_count} products were successfully updated.",
            messages.SUCCESS
        )


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = ["title", "products_count"]

    # /admin/store/product/?collection__id=6
    @admin.display(ordering="products_count")
    def products_count(self, collection):
        # reverse("admin:app_model_page")
        url = (reverse("admin:store_product_changelist")
               + "?"
               + urlencode({
                    "collection__id": str(collection.id)
                }))
        return format_html("<a href='{}'>{}</a>", url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count("product"))


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', "membership", "orders"]
    list_display_links = ['first_name']
    list_editable = ['membership']
    list_per_page = 10
    list_select_related = ["user"]
    ordering = ["user__first_name", "user__last_name"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    @admin.display(ordering="user__first_name")
    def first_name(self, customer: models.Customer):
        return customer.user.first_name

    @admin.display(ordering="user__last_name")
    def last_name(self, customer: models.Customer):
        return customer.user.last_name

    # reverse("admin:app_model_page")
    def orders(self, customer):
        url = (reverse("admin:store_order_changelist")
               + "?"
               + urlencode({
                    "customer__id": str(customer.id)
                }))
        return format_html("<a href='{}'>{}</a>", url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count("order")
        )


class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [
            ("<10", "Low")
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    autocomplete_fields = ["product"]
    min_num = 1
    max_num = 10
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    autocomplete_fields = ["customer"]
    list_display = ["id", "customer",
                    "placed_at", "payment_status", "products"]
    list_display_links = ["id"]
    list_editable = ["payment_status"]
    list_per_page = 10

    def products(self, order):
        url = (reverse("admin:store_orderitem_changelist")
               + "?"
               + urlencode({
                    "order__id": str(order.id)
                }))

        return format_html("<a href='{}'>{}</a>", url, order.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count("orderitem__product"))


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["product", "quantity", "unit_price", "order"]
    list_display_links = ["product"]
    list_editable = ["quantity"]
    list_per_page = 10


@admin.register(models.Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ["description", "discount"]
    list_per_page = 10


@admin.register(models.CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["product", "created_at", "quantity"]
    list_per_page = 10

    def created_at(self, cart_item: models.CartItem):
        return cart_item.cart.created_at


class CartItemInline(admin.TabularInline):
    model = models.CartItem
    autocomplete_fields = ["product"]
    min_num = 1
    max_num = 10
    extra = 0


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "formatted_created_at", "cartitem_quantity"]
    list_per_page = 10
    inlines = [CartItemInline]
    readonly_fields = ["id", "formatted_created_at"]

    def formatted_created_at(self, cart: models.Cart):
        return cart.created_at

    def cartitem_quantity(self, cart: models.Cart):
        return cart.cartitem__quantity

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(cartitem__quantity=Sum("cartitem__quantity"))


admin.site.register(models.Address)
