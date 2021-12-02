# django的cbv中最常用也是最底层的view
from django.views.generic.base import View
from goods.models import Goods
import json


# ListView也是比较常用的
# from django.views.generic import ListView


class GoodsListView(View):
    def get(self, request):
        """
        通过django实现商品列表页
        """
        json_list = []
        goods = Goods.objects.all()[:10]
        # for good in goods:
        #     json_dict = {}
        #     json_dict["name"] = good.name
        #     json_dict["category"] = good.category.name
        #     json_dict["market_price"] = good.market_price
        #     json_dict["add_time"] = good.add_time
        #     json_list.append(json_dict)

        # 将model对象转成dict
        # from django.forms.models import model_to_dict
        # for good in goods:
        #     json_dict = model_to_dict(good)
        #     json_list.append(json_dict)
        # 使用jsondumps不能将imagefield和datetimefield序列化，会报错

        from django.core import serializers
        json_data = serializers.serialize("json", goods)
        json_data = json.loads(json_data)
        from django.http import HttpResponse,JsonResponse
        return JsonResponse(json_data,safe=False)
