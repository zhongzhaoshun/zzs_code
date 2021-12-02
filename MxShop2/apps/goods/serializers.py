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
from goods.models import Goods, GoodsCategory
from goods.models import GoodsImage


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
        fields = ['image',]


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
