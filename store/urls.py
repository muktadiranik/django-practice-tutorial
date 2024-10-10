from django.urls import path, include
from rest_framework_nested import routers

from . import query_views
# from . import mixins_views
from . import views

router = routers.DefaultRouter()
router.register("products", views.ProductViewSet, basename="products")
router.register("collections", views.CollectionViewSet, basename="collections")
router.register("customers", views.CustomerViewSet, basename="customers")
router.register("carts", views.CartViewSet, basename="carts")
router.register("orders", views.OrderViewSet, basename="orders")

products_router = routers.NestedSimpleRouter(
    router, "products", lookup="product")

products_router.register("reviews", views.ReviewViewSet,
                         basename="product-reviews")

products_router.register(
    "images", views.ProductImageViewSet, basename="product-images")


carts_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")

carts_router.register("items", views.CartItemViewSet, basename="cart-items")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(products_router.urls)),
    path("", include(carts_router.urls)),

    # path("collections/<int:pk>/", mixins_views.CollectionDetail.as_view(),
    #      name="collection-detail"),
    # path("customers/", mixins_views.CustomerList.as_view()),
    # path("products/<int:pk>/", mixins_views.ProductDetail.as_view()),
    # path("collections/", mixins_views.CollectionList.as_view()),
    # path("products/", mixins_views.ProductList.as_view()),

    path("query/", query_views.query_database),
    path("create/", query_views.create_object),
    path("update/", query_views.update_object),
    path("delete/", query_views.delete_object),
    path("transaction/", query_views.transaction_object),
    path("sql/", query_views.raw_sql)
]
