from django.urls import path
from . import views

urlpatterns = [
    path('api/categories/<str:category_name>/products', views.TopProductsAPIView.as_view(), name='get_top_products'),
    path('api/categories/<str:category_name>/products/<str:product_id>', views.ProductDetailsAPIView.as_view(), name='get_product_details'),
]
