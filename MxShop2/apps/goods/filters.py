import django_filters
from .models import Goods
from django.db.models import Q


class GoodsFilter(django_filters.rest_framework.FilterSet):
    """商品的过滤类"""
    # name是作用在那个字段上
    # lookup_expr就会执行Goods.objects.filter(shop_price__get=),get是大于等于
    pricemin = django_filters.NumberFilter(field_name="shop_price", lookup_expr="gte")
    pricemax = django_filters.NumberFilter(field_name="shop_price", lookup_expr="lte")
    # 要和前段的字段保持一直
    top_category = django_filters.NumberFilter(method="top_category_filter")

    def top_category_filter(self, queryset, name, value):
        """
        查找第一类别下的所有商品
        category_id等于传递过来的value，或者category_id的父category_id等于value，或者category_id的父category_id的父category_id等于value
        """

        return queryset.filter(Q(category_id=value) | Q(category__parent_category_id=value) | Q(
            category__parent_category__parent_category_id=value))

    class Meta:
        # 指明要过滤那个模型
        model = Goods
        # 要和前端页面对应
        fields = ['pricemin', 'pricemax','is_hot']
