from rest_framework import serializers
from goods.models import Goods, GoodsCategory
from django.contrib.auth import get_user_model
import re
from MxShop2.settings import REGEX_MOBILE
from datetime import datetime, timedelta
from .models import VerifyCode
from rest_framework.validators import UniqueValidator

User = get_user_model()


class SmsSerializer(serializers.Serializer):
    # 手机号
    mobile = serializers.CharField(max_length=11, )

    def validate_mobile(self, mobile):
        """
        验证手机号码
        """
        # 手机是否注册，查询UserProfile表是否有记录，有记录就抛出异常
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户已存在")

        # 验证手机号是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码格式有误")

        # 验证手机号码上一次短信发送时间
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        # 判断添加时间是否在当前时间的一分钟之内
        if VerifyCode.objects.filter(add_time__gt=one_mintes_ago, mobile=mobile).count():
            raise serializers.ValidationError("短信发送频繁，一分钟后重试")
        # 短信发送成功，直接返回
        return mobile


# 用户详情serializer
class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    姓名，出生日期，性别，邮箱，手机号
    """

    class Meta:
        model = User
        fields = ("name", "brithday", "mobile", "gender", "email")


# SmsSerializer发送短信验证码的时候，code前端没有传递过来，并且code是必填字段，所以不适合用ModelSerializer
class UserRegSerializer(serializers.ModelSerializer):
    # code在UserProfile没有定义，所以要自己添加
    code = serializers.CharField(required=True, max_length=4, min_length=4, write_only=True, label="验证码",
                                 error_messages={
                                     "required": "请输入验证码",
                                     "blank": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误",
                                 }, help_text="验证码")

    # 验证用户是否存在
    # 在DRF官方文档里的APIGuide下的Vlidators下的UniqueTogetherValidator
    username = serializers.CharField(label="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])
    # 设置密码为密文
    password = serializers.CharField(label="密码", style={'input_type': 'password'}, write_only=True)

    # 重载create方法，进行密码加密
    # def create(self, validated_data):
    #     # 这样执行后能去到一个user
    #     user = super(UserRegSerializer, self).create(validated_data=validated_data)
    #     # 在UserPerfile里继承了AbstractUser，点进去后有一个AbstractBaseUser，点进去后下滑可以找到set_password方法，可以直接拿来用
    #     user.set_password(validated_data["password"])
    #     user.save()
    #     return user

    def validated_code(self, code):

        # 这样写起来更加简洁，但是这种方式会抛出异常，因为有可能随机字符串两次随机到了一样的，就回有可能返回多条数据，
        # verify_records = VerifyCode.objects.get(mobile=self.initial_data["username"],code=code)

        # 验证手机号码上一次短信发送时间
        # 验证码出错的可能，验证码错误，长度不对，验证码过期，填写的前一个验证码
        # 判断验证码是否时效,用户post过来的值都在initial_data里
        # print("-------------------------------{}".format(self.initial_data["username"]))
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")
        # 如果找到验证码,进行验证码校验
        if verify_records:
            last_records = verify_records[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            # 如果五分钟前的时间小于最后发送的时间,就说明验证码过期
            if five_mintes_ago > last_records:
                raise serializers.ValidationError("验证码过期")

            if last_records.code != code:
                raise serializers.ValidationError("验证码错误")
        #  如果没找到验证码
        else:
            raise serializers.ValidationError("验证码错误")

    def validate(self, attrs):
        # 这个validate比较灵活，是作用于所有的serializer至上的，attrs是每个validate之后返回的一个总的dict
        # 将
        attrs["mobile"] = attrs["username"]
        del attrs["code"]
        return attrs

    class Meta:
        model = User
        fields = ("username", "code", "mobile", "password")


