# -*- encoding: utf-8 -*-
'''
@File    :   filters.py   
@Contact :   nick623738321@163.com
@Author  :    zzs
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/9/1 22:40   zzs         1.0          None
'''

from rest_framework import generics
from django_filters import rest_framework as filters
# from myapp import Product
from .models import Goods
from django.db.models import Q


# 商品过滤器
class GoodsFilter(filters.FilterSet):
    """
    商品的过滤类
    """
    # 和前端对应
    pricemin = filters.NumberFilter(field_name='shop_price', lookup_expr='gte')
    pricemax = filters.NumberFilter(field_name='shop_price', lookup_expr='lte')
    top_category = filters.NumberFilter(method='top_category_filter')

    def top_category_filter(self, queryset, name, value):
        # Goods的商品类目等于传递过来的value，或category外键的parent_category的id等于传递过来的value，或category外键的parent_category的parent_category_id等于传递过来的value
        # 总的来说，查询一二三级目录下的匹配数据
        return queryset.filter(Q(category_id=value) | Q(category__parent_category_id=value) | Q(
            category__parent_category__parent_category_id=value))

    class Meta:
        model = Goods
        fields = ['pricemin', 'pricemax']
