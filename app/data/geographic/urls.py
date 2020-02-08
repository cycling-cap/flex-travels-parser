from django.conf.urls import url
from django.urls import path

from .views import city_list, province_list

geographic_urlpatterns = [
    path('api/geographic/cities/', city_list),
    path('api/geographic/provinces/', province_list),
    url(r'api/geographic/provinces/(?P<province_key>[0-9]+)/cities', city_list),
]
