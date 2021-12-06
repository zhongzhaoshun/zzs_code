# -*- encoding: utf-8 -*-
'''
@File    :   serializers.py
@Contact :   nick623738321@163.com
@Author  :    zzs
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/10/9 22:04   zzs         1.0          None
'''
from rest_framework import serializers
from goods.models import Goods, GoodsCategory, Banner, GoodsCategoryBrand, IndexAd
from goods.models import GoodsImage
from django.db.models import Q


# 三类列表
class CategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


# 二级列表
class CategorySerializer2(serializers.ModelSerializer):
    sub_cat = CategorySerializer3(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


# 如果要显示查询结果里外键的内容，就再添加一个serializer
class CategorySerializer(serializers.ModelSerializer):
    # sub_cat要和GoodsCategory的parent_category的related_name保持一致
    # 一定要加一个many=True参数，说明可能结果会有多个，不加的话可能会报错
    sub_cat = CategorySerializer2(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


# 商品轮播图的serializer
class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ['image', ]


# ModelSerializer省去了所有查询字段的添加
class GoodsSerializer(serializers.ModelSerializer):
    # 将查询出来的外键结果，覆盖掉默认的
    category = CategorySerializer()
    images = GoodsImageSerializer(many=True)

    class Meta:
        # 序列化goods模型
        model = Goods
        # 指定要序列化模型的属性，如果要查询所有属性，就把查询的列表改为"__all__"
        # fields = ['name', 'click_num', 'market_price', 'add_time']
        fields = "__all__"


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = "__all__"


class IndexCategorySerializer(serializers.ModelSerializer):
    # 实际上是brand的表有一个外键指向category，一个category可能会有很多个brand，所以要加上many=true
    brands = BrandSerializer(many=True)
    # 使用自定义的方法，获取商品
    goods = serializers.SerializerMethodField()
    # 获取二级商品,上面也写过，直接复制过来
    sub_cat = CategorySerializer2(many=True)
    # 再取数据的时候进行一下序列化
    ad_goods = serializers.SerializerMethodField()

    def get_ad_goods(self, obj):
        goods_json = {}
        ad_goods = IndexAd.objects.filter(category_id=obj.id)
        if ad_goods:
            goods_ins = ad_goods[0].goods
            goods_json = GoodsSerializer(goods_ins, many=False,context={"request":self.context["request"]}).data
        return goods_json

    # get_加上fields的名
    def get_goods(self, obj):
        # 之前在goods的filters里用过，直接复制过来就行
        all_goods = Goods.objects.filter(Q(category_id=obj.id) | Q(category__parent_category_id=obj.id) | Q(
            category__parent_category__parent_category_id=obj.id))
        #  对查询结果进行序列化,只要把查询出来的query_set传进来，然后返回.data就可以了
        goods_serializer = GoodsSerializer(all_goods, many=True,context={"request":self.context["request"]})
        return goods_serializer.data

    class Meta:
        model = GoodsCategory
        fields = "__all__"
