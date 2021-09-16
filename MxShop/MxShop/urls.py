"""MxShop URL Configuration

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
from django.conf.urls import url, include
import xadmin
from MxShop.settings import MEDIA_ROOT
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from goods.views import GoodsListViewset, CategoryViewset
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token
from users.views import SmsCodeViewset,UserViewset

# 先生成一个router对象
router = DefaultRouter()

# 配置goods的url，配置这个url之后，就不用配置urlpatterns
# 以后大部分的url都会基于router来配置
router.register(r'goods', GoodsListViewset, basename="goods")

# 配置category的url
router.register(r'categorys', CategoryViewset, basename="categorys")

# 短信验证码
router.register(r'codes', SmsCodeViewset, basename="codes")


router.register(r'users', UserViewset, basename="users")

# 使用了router就不用自己绑定了
# goods_list = GoodsListViewset.as_view({
#     # 可以将get请求绑定到list之上
#     'get': 'list',
# })


urlpatterns = [
    path('admin/', admin.site.urls),
    # router要加上这个url
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    url(r'^xadmin/', xadmin.site.urls),
    url(r"^media/(?P<path>.*)$", serve, {"document_root": MEDIA_ROOT}),
    # 商品列表
    url(r'docs/$', include_docs_urls(title="生鲜项目")),
    # DRF自带的token认证
    path('api-token-auth/', views.obtain_auth_token),
    # JTW的认证接口
    url(r'^login/', obtain_jwt_token),

]
