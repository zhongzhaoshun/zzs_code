from rest_framework.pagination import PageNumberPagination

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Goods, GoodsCategory, Banner
from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .filters import GoodsFilter
from rest_framework import filters
from rest_framework.authentication import TokenAuthentication

from .serializers import GoodsSerializer, CategorySerializer, BannerSerializer, IndexCategorySerializer


# Create your views here.

# 设置分页信息
class GoodsPagination(PageNumberPagination):
    # 每页多少条
    page_size = 12
    # 指明向后台要多少条
    page_size_query_param = 'page_size'
    # 下一页标识
    page_query_param = "page"
    # 最多分多少页
    max_page_size = 100


# GenericAPIView底层还是实现的APIview，还有一个mixins.CreateModelMixin，因为这个项目是后台添加商品的，不用用户添加商品，所以不用这个view了
class GoodsListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    商品列表，搜索，过滤，分页，排序
    """

    # 使用了DRF的filter就不用写get_queryset函数了
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    # 将分页信息加载进来
    pagination_class = GoodsPagination
    # authentication_classes = (TokenAuthentication,)
    # 使用DRF的filter
    # 配置搜索，要增加一个filters.SearchFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = GoodsFilter
    # 配置要搜索的字段
    search_fields = ['name', 'goods_brief', "goods_desc"]
    # 要排序的字段
    ordering_fields = ['sold_num', 'shop_price']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        商品分类列表数据
    retrieve:
        获取商品分类数据
    """
    # 获取所有数据
    # queryset = GoodsCategory.objects.all()
    # 获取一类数据
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer


class BannerViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """获取轮播图列表"""
    queryset = Banner.objects.all().order_by("index")
    serializer_class = BannerSerializer


class IndexCategoryViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """首页商品分类数据"""
    # 只获取两种
    queryset = GoodsCategory.objects.filter(is_tab=True, name__in=["生鲜食品", "酒水饮料"])
    serializer_class = IndexCategorySerializer
