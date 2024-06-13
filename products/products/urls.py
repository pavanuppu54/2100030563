from django.urls import path
from . import views
urlpatterns = [
    path("categories/<str:category_name>/products",views.top_products ,name='top_products'),
    path("categories/<str:category_name>/products/<str:product_id>",views.product_detail ,name='product_detail'),
]
