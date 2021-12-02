# -*- encoding: utf-8 -*-
'''
@File    :   import_category_data.py   
@Contact :   nick623738321@163.com
@Author  :    zzs
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/10/3 19:04   zzs         1.0          None
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

from goods.models import GoodsCategory
from db_tools.data.category_data import row_data

for lev1_cat in row_data:
    lev1_instance = GoodsCategory()
    lev1_instance.code = lev1_cat["code"]
    lev1_instance.name = lev1_cat["name"]
    lev1_instance.category_type = 1
    lev1_instance.save()

    for lev2_cat in lev1_cat["sub_categorys"]:
        lev2_instance = GoodsCategory()
        lev2_instance.code = lev2_cat["code"]
        lev2_instance.name = lev2_cat["name"]
        lev2_instance.category_type = 2
        lev2_instance.parent_category = lev1_instance
        lev2_instance.save()

        for lev3_cat in lev2_cat["sub_categorys"]:
            lev3_instance = GoodsCategory()
            lev3_instance.code = lev3_cat["code"]
            lev3_instance.name = lev3_cat["name"]
            lev3_instance.category_type = 3
            lev3_instance.parent_category = lev2_instance
            lev3_instance.save()
