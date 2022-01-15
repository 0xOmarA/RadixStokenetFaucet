from django.urls import re_path
from .views import xrd_request, wallet_balance, faucet_homepage

urlpatterns = [
    re_path(r'^/?$', faucet_homepage),
    re_path(r'^xrd_request/?$', xrd_request),
    re_path(r'^wallet_balance/?$', wallet_balance),
]
