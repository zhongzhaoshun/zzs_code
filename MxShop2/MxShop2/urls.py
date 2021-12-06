"""MxShop2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import xadmin
from django.conf.urls import url, include
from MxShop2.settings import MEDIA_ROOT
# 专门用来做静态文件的serve
from django.views.static import serve
# 引入drf的文档
from rest_framework.documentation import include_docs_urls
from goods.views import GoodsListViewSet, CategoryViewSet,BannerViewset,IndexCategoryViewset
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token
from users.views import SmsCodeViewset, UserViewSet
from user_operation.views import UserFavViewset, LeavingMessageViewSet, AddressViewSet
from trade.views import ShoppingCartViewset, OrderViewSet
from trade.views import AliPayView
from django.views.generic import TemplateView

# 先生成一个router对象
router = DefaultRouter()
# 配置goods的url
router.register(r'goods', GoodsListViewSet, basename="goods")

# 配置category的url
router.register(r'categorys', CategoryViewSet, basename="categorys")
# 短信发送的url
router.register(r'codes', SmsCodeViewset, basename="codes")
# 用户注册
router.register(r'users', UserViewSet, basename="users")
# 用户收藏
router.register(r'userfavs', UserFavViewset, basename="userfavs")
# 用户留言
router.register(r'messages', LeavingMessageViewSet, basename="messages")
# 用户收货地址
router.register(r'address', AddressViewSet, basename="address")
# 购物车
router.register(r'shopcarts', ShoppingCartViewset, basename="shopcarts")
# 用户订单
router.register(r'orders', OrderViewSet, basename="orders")
# 轮播图
router.register(r'banners', BannerViewset, basename="banners")
# 首页商品分类数据
router.register(r'indexGoods', IndexCategoryViewset, basename="indexGoods")

# goods_list = GoodsListViewSet.as_view({
#     'get': 'list',
# })

urlpatterns = [
    # path('admin/', admin.site.urls),
    url(r"^xadmin/", xadmin.site.urls),
    # 配置访问静态图片
    url(r"^media/(?P<path>.*)$", serve, {"document_root": MEDIA_ROOT}),
    # drf登陆的url，调试api的时候会用到
    path('api-auth/', include('rest_framework.urls')),
    # 获取token的url,DRF自带的tokwn认证模式
    path('api-token-auth/', views.obtain_auth_token),

    # 配置router的url
    path('', include(router.urls)),
    # indexurl
    url(r'^index/', TemplateView.as_view(template_name="index.html"),name="index"),
    # 使用drf文档
    url(r"docs/", include_docs_urls(title="Fresh")),
    # JWT的认证接口
    url(r'^login', obtain_jwt_token),

    url(r"^alipay/return", AliPayView.as_view(), name="alipay")

]
