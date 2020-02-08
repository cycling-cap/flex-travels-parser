import os

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from base.http import AlpsRestResponse
import json

from entry import settings


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def province_list(request):
    with open(settings.STATIC_ROOT + '/province.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    return AlpsRestResponse.success(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def city_list(request, province_key):
    with open(settings.STATIC_ROOT + '/city.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    ret = {k: v for k, v in data.items() if k == province_key}
    if ret and len(ret) > 0:
        ret = ret[province_key]
    else:
        ret = []

    return AlpsRestResponse.success(ret)

