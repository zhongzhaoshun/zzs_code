from rest_framework import serializers
from .models import Goods, ShoppingCart, OrderInfo, OrderGoods
from goods.serializers import GoodsSerializer
from utils.alipay import AliPay
from MxShop2 import settings
import time
import random


class ShopCartDetailSerializer(serializers.ModelSerializer):
    # 因为一个商品只能有一个记录
    goods = GoodsSerializer(many=False, read_only=True)

    class Meta:
        model = ShoppingCart
        # fields = ("goods", "nums")
        fields = "__all__"


class ShopCartSerializer(serializers.Serializer):
    # 获取当前登陆的用户
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    nums = serializers.IntegerField(required=True, min_value=1,
                                    error_messages={"min_value": "商品数量不能小于1", "required": "请选择购买数量", })
    # 外键
    goods = serializers.PrimaryKeyRelatedField(queryset=Goods.objects.all(), required=True)

    # 重点！！！
    def create(self, validated_data):
        print(validated_data)
        print(validated_data["nums"])
        # validated_data的方法的数据是每个变量已经做过validate处理的数据，
        user = self.context["request"].user
        nums = validated_data["nums"]
        goods = validated_data["goods"]
        existed = ShoppingCart.objects.filter(user=user, goods=goods)
        if existed:
            # 获取第一条记录
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            #     如果商品已经存在
            # 接收一下返回值，要做反序列化
            shopcart = ShoppingCart.objects.create(**validated_data)
        return existed

    # instance实际上就是传递过来的ShoppingCart
    def update(self, instance, validated_data):
        # 修改商品数量
        instance.nums = validated_data["nums"]
        instance.save()
        return instance


class OrderSerializer(serializers.ModelSerializer):
    # 不能修改用户
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    pay_status = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)

    # 只读形式的，不可能将生成的URL返回给用户的
    alipay_url = serializers.SerializerMethodField(read_only=True)

    # 规则：在字段前加一个get_,object就是serializer对象，这样写，初始化的时候就可以生成支付宝的url了
    def get_alipay_url(self, obj):
        # 在这里就可以生成支付宝的url了,支付宝的url之前写过了，直接复制过来就行
        alipay = AliPay(
            # 首先要传一个appid，在沙箱里可以找到
            appid="2016101800713825",
            # 默认的就行
            # app_notify_url是用于用户扫码后没有支付，关闭了页面，然后用户到手机账单里面支付，也就是不是在浏览器页面上支付的，支付宝会发送一个异步的接口，返回支付结果
            app_notify_url="http://127.0.0.1:8000/alipay/return",
            # 自己私钥的路径，也可以写相对路径
            app_private_key_path=settings.private_key_path,
            # 支付宝的公钥，验证支付宝回传消息使用，不是自己的公钥,
            alipay_public_key_path=settings.ali_pub_key_path,
            # app_private_key_path=app_private_key_path_string,
            # alipay_public_key_path=alipay_public_key_path_string,
            debug=True,  # 默认False,
            # 支付成功后跳转的页面，但是如果用户不是在页面 支付的话，这个return_url就没有用了，就要用到app_notify_url了
            return_url="http://127.0.0.1:8000/alipay/return"
        )
    #     这里的参数改好之后，直接调用之前写好的逻辑
        url = alipay.direct_pay(
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
            # returnurl不用传了，AliPay的逻辑里有初始化url

        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
        return re_url

    def generate_order_sn(self):
        # 生成订单号，当前时间+userid+随机数
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context["request"].user.id,
                                                       ranstr=random.randint(10, 99))
        return order_sn

    # 复制订单号
    def validate(self, attrs):
        attrs["order_sn"] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = "__all__"


class OrderGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = "__all__"


class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerializer(many=True)
    # 因为个人中心的订单页面里，有订单的详细信息，支付记录，而且订单状态如果是待支付，有一个按钮是跳转到支付宝支付的，可以直接把url放到里面
    # 只读形式的，不可能将生成的URL返回给用户的
    alipay_url = serializers.SerializerMethodField(read_only=True)

    # 规则：在字段前加一个get_,object就是serializer对象，这样写，初始化的时候就可以生成支付宝的url了
    def get_alipay_url(self, obj):
        # 在这里就可以生成支付宝的url了,支付宝的url之前写过了，直接复制过来就行
        alipay = AliPay(
            # 首先要传一个appid，在沙箱里可以找到
            appid="2016101800713825",
            # 默认的就行
            # app_notify_url是用于用户扫码后没有支付，关闭了页面，然后用户到手机账单里面支付，也就是不是在浏览器页面上支付的，支付宝会发送一个异步的接口，返回支付结果
            app_notify_url="http://127.0.0.1:8000/alipay/return",
            # 自己私钥的路径，也可以写相对路径
            app_private_key_path=settings.private_key_path,
            # 支付宝的公钥，验证支付宝回传消息使用，不是自己的公钥,
            alipay_public_key_path=settings.ali_pub_key_path,
            # app_private_key_path=app_private_key_path_string,
            # alipay_public_key_path=alipay_public_key_path_string,
            debug=True,  # 默认False,
            # 支付成功后跳转的页面，但是如果用户不是在页面 支付的话，这个return_url就没有用了，就要用到app_notify_url了
            return_url="http://127.0.0.1:8000/alipay/return"
        )
        #     这里的参数改好之后，直接调用之前写好的逻辑
        url = alipay.direct_pay(
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
            # returnurl不用传了，AliPay的逻辑里有初始化url

        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
        return re_url

    class Meta:
        model = OrderInfo
        fields = "__all__"
