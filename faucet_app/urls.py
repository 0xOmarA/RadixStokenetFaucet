from django.urls import re_path
from .views import xrd_request, wallet_balance

urlpatterns = [
    re_path(r'^xrd_request/?$', xrd_request),
    re_path(r'^wallet_balance/?$', wallet_balance)
]
