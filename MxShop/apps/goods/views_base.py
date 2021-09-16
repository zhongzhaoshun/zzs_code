# -*- encoding: utf-8 -*-
'''
@File    :   views_base.py   
@Contact :   nick623738321@163.com
@Author  :    zzs
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/8/24 16:55   zzs         1.0          None
'''

from django.views.generic.base import View
from goods.models import Goods
from django.http import HttpResponse, JsonResponse
import json
from django.forms.models import model_to_dict
from django.core import serializers


class GoodsListView(View):
    def get(self, request):
        # 通过django实现商品列表页
        json_list = []
        goods = Goods.objects.all()[:10]
        # for good in goods:
        #     json_dict = {}
        #     json_dict['name'] = good.name
        #     json_dict['category'] = good.category.name
        #     json_dict['market_price'] = good.market_price
        #     json_list.append(json_dict)

        # for good in goods:
        #     json_dict = model_to_dict(good)
        #     json_list.append(json_dict)

        json_data = serializers.serialize("json", goods)
        # json_data = json.loads(json_data)
        return HttpResponse(json_data, content_type='application/json')
