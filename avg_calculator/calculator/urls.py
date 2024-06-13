from django.urls import path
from .views import NumberAPIView

urlpatterns = [
    path('<str:numberid>/', NumberAPIView.as_view(), name='get_numbers'),
]
