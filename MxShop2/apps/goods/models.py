from django.db import models
from datetime import datetime
from DjangoUeditor.models import UEditorField


# Create your models here.

# 商品类别
class GoodsCategory(models.Model):
    """商品类别"""
    CATEGORY_TYPE = (
        (1, "一级类目"),
        (2, "二级类目"),
        (3, "三级类目"),
    )
    # 商品名
    name = models.CharField(default="", max_length=30, verbose_name="类别名", help_text="类别名")
    # 商品编码
    code = models.CharField(default="", max_length=30, verbose_name="类别code", help_text="类别code")
    # 商品描述
    desc = models.TextField(default="", verbose_name="类别描述", help_text="类别描述")
    # 商品分类
    category_type = models.IntegerField(choices=CATEGORY_TYPE, verbose_name="类目级别", help_text="类目级别")
    # self指向当前类
    parent_category = models.ForeignKey("self", null=True, blank=True, verbose_name="父类目级别", help_text="父类目级别",
                                        on_delete=models.CASCADE, related_name="sub_cat")
    # 是否放到页面
    is_tab = models.BooleanField(default=False, verbose_name="是否导航", help_text="是否导航")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "商品类别"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 品牌
class GoodsCategoryBrand(models.Model):
    """品牌名"""
    category = models.ForeignKey(GoodsCategory, null=True, blank=True, related_name="brands", verbose_name="商品名称",
                                 on_delete=models.CASCADE)
    # 品牌名
    name = models.CharField(default="", max_length=30, verbose_name="品牌名", help_text="品牌名")
    # 品牌描述
    desc = models.CharField(default="", max_length=200, verbose_name="品牌描述", help_text="品牌描述")
    # 商品图片
    image = models.ImageField(max_length=200, upload_to="brands/")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "品牌"
        verbose_name_plural = verbose_name
        db_table = "goods_goodsbrand"

    def __str__(self):
        return self.name


# 商品
class Goods(models.Model):
    """商品"""
    # 商品类别，外键指向GoodsCategory
    category = models.ForeignKey(GoodsCategory, verbose_name="商品类目", on_delete=models.CASCADE)
    # 商品编码
    goods_sn = models.CharField(max_length=30, default="", verbose_name="商品唯一货号")
    # 商品名
    name = models.CharField(max_length=300, verbose_name="商品名")
    # 商品点击数
    click_num = models.IntegerField(default=0, verbose_name="商品点击数")
    # 卖出的数量
    sold_num = models.IntegerField(default=0, verbose_name="商品销售量")
    # 收藏数
    fav_num = models.IntegerField(default=0, verbose_name="收藏数")
    # 库存
    goods_num = models.IntegerField(default=0, verbose_name="库存")
    # 商品市场价
    market_price = models.FloatField(default=0, verbose_name="市场价格")
    # 商店价格
    shop_price = models.FloatField(default=0, verbose_name="本店价格")
    # 商品简介
    goods_brief = models.TextField(max_length=500, verbose_name="商品简短描述")
    # 商品富文本描述
    goods_desc = UEditorField(verbose_name=u"内容", imagePath="goods/images/", width=1000, height=300,
                              filePath="goods/files/", default="")
    # 是否免运费
    ship_free = models.BooleanField(default=True, verbose_name="是否承担运费")
    # 封面图片
    goods_front_image = models.ImageField(upload_to="goods/images/", null=True, blank=True, verbose_name="封面图")
    # 是否为新品
    is_new = models.BooleanField(default=False, verbose_name="是否新品")
    # 热卖商品
    is_hot = models.BooleanField(default=False, verbose_name="是否热销")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")


# 在首页里显示的广告位
class IndexAd(models.Model):
    category = models.ForeignKey(GoodsCategory, related_name="category", verbose_name="商品类目", on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, related_name="goods", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "首页商品类别广告"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods.name


# 商品图片
class GoodsImage(models.Model):
    """商品轮播图"""
    goods = models.ForeignKey(Goods, verbose_name="商品", related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="", verbose_name="图片", null=True, blank=True)
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "商品图片"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods.name


# 轮播商品
class Banner(models.Model):
    """轮播商品"""
    goods = models.ForeignKey(Goods, verbose_name="商品", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="banner", verbose_name="轮播图片")
    index = models.IntegerField(default=0, verbose_name="轮播顺序")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "轮播商品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods.name
