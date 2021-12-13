from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from utils.permissions import IsOwnerOrReadOnly
from .serializer import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from .models import ShoppingCart, OrderGoods, OrderInfo
from rest_framework import mixins
from utils.alipay import AliPay
from MxShop2 import settings
from rest_framework.response import Response
from django.shortcuts import redirect
import time
from datetime import datetime

import random


# Create your views here.

class ShoppingCartViewset(viewsets.ModelViewSet):
    """
    购物车功能
    list:
        获取购物车详情
    create：
        加入购物车
    delete：
        删除购物记录
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    serializer_class = ShopCartSerializer
    # 一定要加，很容易被忽略
    queryset = ShoppingCart.objects.all()
    lookup_field = "goods_id"

    # 商品添加到购物车，库存数就减
    def perform_create(self, serializer):
        shop_cart = serializer.save()
        # 因为serializer里用的是ShoppingCart
        goods = shop_cart.goods
        goods.goods_num -= shop_cart.nums
        goods.save()

    # 用户删除购物车商品，也会修改商品库存，这里重写的是mixins.DestroyModelMixin方法
    def perform_destroy(self, instance):
        # goods一定要在删除之前取
        goods = instance.goods
        goods.goods_num += instance.nums
        goods.save()
        instance.delete()

    # 用户更新购物车商品数量时候，也会修改商品库存，这里重写的是 mixins.UpdateModelMixin方法
    # 这里比较重要了，因为有可能是增加，或者减少
    def perform_update(self, serializer):
        # 获取到已有的值
        existed_record = ShoppingCart.objects.get(id=serializer.instance.id)
        # 获取到保存之前的值
        existed_nums = existed_record.nums
        # 获取保存之后的值
        saved_record = serializer.save()
        # 如果nums大于0，也就是保存之后的值大于保存之前的值，也就是进行了增的操作，如果修改后的数量小于修改前的数量，就是进行了减的操作
        nums = saved_record.nums - existed_nums
        goods = saved_record.goods
        goods.goods_num -= nums
        goods.save()

    # 动态生成serializer
    def get_serializer_class(self):
        if self.action == "list":
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer

    # 只返回当前用户的列表
    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)


class OrderViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.DestroyModelMixin):
    """
    订单管理：
    list：
        获取所有订单
    delete：
        删除订单
    create：
        新增订单
    """

    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer

    # 生成订单号，并获取购物车所有商品
    def perform_create(self, serializer):
        # 因为订单号在serial里写好了，这里可以直接保存了
        order = serializer.save()
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        # 有了这些信息就能生成OrderViewSet的表了
        for shop_cart in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_goods.order = order
            order_goods.save()
            # 删除购物车商品
            shop_cart.delete()
        return order


class AliPayView(APIView):
    # 视频里的是alipay支付完成后返回的是post请求，但是实际上写的是get请求
    def get(self, request):
        """
        处理支付宝的returnurl返回
        """
        print("访问了GET")
        process_dict = {}
        # 把全部数据取出来放到字典里
        for key, value in request.GET.items():
            process_dict[key] = value

        # 因为urlparse的话，里面的数据汇变成lsit，只取了弟0个
        # 删除了字典里的sign
        sign = process_dict.pop("sign", None)  # 将alipa的一断代码直接复制过来
        alipay = AliPay(
            appid=settings.alipay_appid,
            app_notify_url="http://127.0.0.1:8000/index/#/app/home/member/order",
            # 因为这个路径写绝对路径很容易出错的，所以在settings里写一个相对路径
            app_private_key_path=settings.private_key_path,
            alipay_public_key_path=settings.ali_pub_key_path,
            debug=True,  # 默认False,
            return_url="http://127.0.0.1:8000/index/#/app/home/member/order"
        )
        # 进行支付结果验证
        verify = alipay.verify(process_dict, sign)
        print(process_dict)
        if verify is True:
            # 支付宝接口返回的商户网站唯一订单号
            order_sn = process_dict.get("out_trade_no", None)
            # 支付宝返回的系统中交易流水号，最长64位
            trade_no = process_dict.get("trade_no", None)
            # 支付宝返回的支付状态
            # trade_stauts = process_dict.get("tradeStatus", None)
            trade_stauts = "TRADE_SUCCESS"
            # 更新数据库的支付信息
            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:

                # 支付成功后，修改商品数量，直接用related_name就能获取到
                order_goods = existed_order.goods.all()
                for order_good in order_goods:
                    # 获取到商品
                    goods = order_good.goods
                    goods.sold_num += order_good.goods_num
                    goods.save()

                # 修改支付状态
                existed_order.pay_status = trade_stauts
                # 支付订单号
                existed_order.trade_no = trade_no
                # 支付时间
                existed_order.pay_time = datetime.now()
                existed_order.save()
            #  支付完成后跳转到支付页面，pay是前段判断的,max_age尽量设置的短一点，让他取一次就失效
            response = redirect("index")
            response.set_cookie("nextPath", "pay", max_age=10)
            print("验证成功")
            return response
        else:
            # 如果支付验证失败了，直接跳转到首页
            response = redirect("index")
            print("验证失败")
            return response

    def post(self, request):
        """
        处理支付宝的notifyurl

        """
        # 先创建一个空字典
        process_dict = {}
        # 把全部数据取出来放到字典里
        for key, value in request.POST.items():
            process_dict[key] = value

        # 因为urlparse的话，里面的数据汇变成lsit，只取了弟0个
        # 删除了字典里的sign
        sign = process_dict.pop("sign", None)

        # 将alipa的一断代码直接复制过来
        alipay = AliPay(
            appid=settings.alipay_appid,
            app_notify_url="http://127.0.0.1:8000/orders",
            # 因为这个路径写绝对路径很容易出错的，所以在settings里写一个相对路径
            app_private_key_path=settings.private_key_path,
            alipay_public_key_path=settings.ali_pub_key_path,
            debug=True,  # 默认False,
            # 其实不写returnurl也可以
            return_url="http://127.0.0.1:8000/orders"
        )
        # 进行支付结果验证
        verify = alipay.verify(process_dict, sign)

        print(verify)
