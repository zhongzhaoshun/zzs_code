# -*- encoding: utf-8 -*-
'''
@File    :   import_category_data.py
@Contact :   nick623738321@163.com
@Author  :    zzs
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/8/23 22:01   zzs         1.0          None
'''

# 独立使用django的model
# import sys
# import os
#
# # 获取当前目录-dbtools
# pwd = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(pwd + '../')
# # 单独使用django的module
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MxShop.settings')
#
# import django
#
# django.setup()
#
# # 一定要在django.setup之后用
# from goods.models import GoodsCategory
# from db_tools.data.category_data import row_data
#
# for lev1_cat in row_data:
#     lev1_instance = GoodsCategory()
#     lev1_instance.code = lev1_cat['code']
#     lev1_instance.name = lev1_cat['name']
#     lev1_instance.category_type = 1
#     lev1_instance.save()
#
#     for lev2_cat in lev1_cat['sub_categorys']:
#         lev2_instance = GoodsCategory()
#         lev2_instance.code = lev2_cat['code']
#         lev2_instance.name = lev2_cat['name']
#         lev2_instance.category_type = 2
#         lev2_instance.parent_category = lev1_instance
#         lev2_instance.save()
#
#         for lev3_cat in lev1_cat['sub_categorys']:
#             lev3_instance = GoodsCategory()
#             lev3_instance.code = lev3_cat['code']
#             lev3_instance.name = lev3_cat['name']
#             lev3_instance.category_type = 3
#             lev3_instance.parent_category = lev2_instance
#             lev3_instance.save()

# -*- coding: utf-8 -*-
__author__ = 'bobby'

#独立使用django的model
import sys
import os


pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd+"../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MxShop.settings")

import django
django.setup()

from goods.models import GoodsCategory

from db_tools.data.category_data import row_data

for lev1_cat in row_data:
    lev1_intance = GoodsCategory()
    lev1_intance.code = lev1_cat["code"]
    lev1_intance.name = lev1_cat["name"]
    lev1_intance.category_type = 1
    lev1_intance.save()

    for lev2_cat in lev1_cat["sub_categorys"]:
        lev2_intance = GoodsCategory()
        lev2_intance.code = lev2_cat["code"]
        lev2_intance.name = lev2_cat["name"]
        lev2_intance.category_type = 2
        lev2_intance.parent_category = lev1_intance
        lev2_intance.save()

        for lev3_cat in lev2_cat["sub_categorys"]:
            lev3_intance = GoodsCategory()
            lev3_intance.code = lev3_cat["code"]
            lev3_intance.name = lev3_cat["name"]
            lev3_intance.category_type = 3
            lev3_intance.parent_category = lev2_intance
            lev3_intance.save()

