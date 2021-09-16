from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Goods, GoodsCategory
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .filters import GoodsFilter
from rest_framework import filters
from .serializers import GoodsSerializer, CategorySerializer
from rest_framework.authentication import TokenAuthentication


# restframework自带的分页
class GoodsPagination(PageNumberPagination):
    page_size = 12
    # page_size指明向后台要多少条
    page_size_query_param = 'page_size'
    # P代表多少页
    page_query_param = "page"
    max_page_size = 100


# 继承GenericAPIView或者apiview，一定要重写get
class GoodsListViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    商品列表页
    """
    # queryset = Goods.objects.all()
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination
    # 设置token验证
    # authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    print(filter_backends)
    filter_class = GoodsFilter
    # ^以**开头的
    # =精确搜索
    # 一些简单的查询操作
    search_fields = ['name', 'goods_brief', 'goods_desc']
    # 查询结果排序
    ordering_fields = ['sold_num', 'shop_price']


# RetrieveModelMixin获取某一个商品详情,加了这个方法，就不用按照restful api规范配置url了
class CategoryViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        商品分类列表数据
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer
