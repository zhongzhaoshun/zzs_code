# -*- encoding: utf-8 -*-
'''
@File    :   serializers.py
@Contact :   nick623738321@163.com
@Author  :    zzs
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/8/24 22:40   zzs         1.0          None
'''
from rest_framework import serializers
from goods.models import Goods, GoodsCategory


# class GoodsSerializer(serializers.Serializer):
#     name = serializers.CharField(required=True, max_length=100)
#     click_num = serializers.IntegerField(default=0)
#     goods_front_image = serializers.ImageField()
#
#     def create(self, validated_data):
#         return Goods.objects.create(**validated_data)


# 三级目录
class CategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


# 二级目录
class CategorySerializer2(serializers.ModelSerializer):
    sub_cat = CategorySerializer3(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


# 一级目录
class CategorySerializer(serializers.ModelSerializer):
    sub_cat = CategorySerializer2(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


# rest_framework自带的ModelSerializer
class GoodsSerializer(serializers.ModelSerializer):
    # 实例化并显示详情
    category = CategorySerializer()

    class Meta:
        model = Goods
        # fields = ['name', 'click_num', 'market_price', 'add_time']
        fields = "__all__"
