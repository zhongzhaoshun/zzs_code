# -*- encoding: utf-8 -*-
'''
@File    :   import_goods_data.py   
@Contact :   nick623738321@163.com
@Author  :    zzs
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/10/3 19:26   zzs         1.0          None
'''
# 独立使用django的model
import sys, os

# 找到当前路径，也就是db_tools路径
pwd = os.path.dirname(os.path.realpath(__file__))
# 将父目录加入进来，也就是MxShop路径
sys.path.append(pwd + '../')
# 很关键，配置使用项目的setting文件
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MxShop2.settings')

import django

django.setup()

from goods.models import Goods, GoodsCategory, GoodsImage
from db_tools.data.product_data import row_data

# 保存商品信息
for goods_detail in row_data:
    goods = Goods()
    goods.name = goods_detail["name"]
    goods.market_price = float(int(goods_detail["market_price"].replace("￥", "").replace("元", "")))
    goods.shop_price = float(int(goods_detail["sale_price"].replace("￥", "").replace("元", "")))
    goods.goods_brief = goods_detail["desc"] if goods_detail["desc"] is not None else ""
    goods.goods_desc = goods_detail["goods_desc"] if goods_detail['goods_desc'] is not None else ""
    goods.goods_front_image = goods_detail["images"][0] if goods_detail["images"] else ""
    category_name = goods_detail["categorys"][-1]
    category = GoodsCategory.objects.filter(name=category_name)
    if category:
        goods.category = category[0]
    goods.save()

    # 保存商品图片信息
    for goods_image in goods_detail["images"]:
        goods_image_instances = GoodsImage()
        goods_image_instances.image = goods_image
        goods_image_instances.goods = goods
        goods_image_instances.save()
