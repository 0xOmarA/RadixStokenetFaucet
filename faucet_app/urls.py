from django.urls import re_path
from .views import xrd_request

urlpatterns = [
    re_path(r'^xrd_request/?$', xrd_request)
]
