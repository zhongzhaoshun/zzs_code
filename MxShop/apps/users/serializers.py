# -*- encoding: utf-8 -*-
'''
@File    :   serializers.py   
@Contact :   nick623738321@163.com
@Author  :    zzs
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/9/9 21:09   zzs         1.0          None
'''

from rest_framework import serializers
from django.contrib.auth import get_user_model
import re
from MxShop.settings import REGEX_MOBILE
from datetime import datetime, timedelta
from .models import VerifyCode
from rest_framework.validators import UniqueValidator

User = get_user_model()


# 验证码
class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11, )

    def validate_mobile(self, mobile):
        """
        验证手机号码
        """
        # 手机是否注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError('用户已存在')
        # 验证手机号码
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码非法")
        # 验证码发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        # 过滤发送时间在当前时间的一分钟之前,如果判断存在记录，说明一分钟之前，这个验证码发送过
        if VerifyCode.objects.filter(add_time__gt=one_mintes_ago, mobile=mobile):
            raise serializers.ValidationError("距离上一次发送时间未超过60秒")
        return mobile


# 用户注册
class UserRegSerializer(serializers.ModelSerializer):
    # 验证码
    code = serializers.CharField(required=True, max_length=4, min_length=4, write_only=True, label="验证码",
                                 error_messages={
                                     "required": "请输入验证码",
                                     "blank": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误",
                                 }, help_text="验证码")

    # 如果验证时报，就用这种方式提示
    username = serializers.CharField(label="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])

    password = serializers.CharField(write_only=True, style={"input_type": "password"}, label="密码")

    # 重载create函数进行密码加密
    # def create(self, validated_data):
    #     # 获取user
    #     user = super(UserRegSerializer, self).create(validated_data=validated_data)
    #     # user.model继承了AbstractUser，AbstractUser里的AbstractUser有set_password
    #     user.set_password(validated_data["password"])
    #     user.save()
    #     return user

    # 验证码校验
    def validate_code(self, code):
        # 使用get方式可能会获取到多条记录,发送验证码很有可能是两次发送了一样的验证码
        # 还有可能获取不到
        # try:
        #     verify_record = VerifyCode.objects.get(mobile=self.initial_data["username"], code=code)
        # except VerifyCode.DoesNotExist:
        #     pass
        # except VerifyCode.MultipleObjectsReturned:
        #     pass

        # 验证码发送频率，用户post过来的值都会放在initial_data里面
        # 根据添加时间排序，获取到用户发送的最新的验证码
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")
        # 如果获取到最新验证码，进行校验
        if verify_records:
            # 获取第一条记录
            last_record = verify_records[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            # 如果当前五分钟之前的时间大于最后一次发送时间，说明验证码已过期
            if five_mintes_ago > last_record.add_time:
                raise serializers.ValidationError("验证码已过期")
            # 如果发送的code不等于传递进来的code，说明验证码有误
            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")

        # 发送记录不存在
        else:
            raise serializers.ValidationError("验证码有误")

    def validate(self, attrs):
        attrs["mobile"] = attrs["username"]
        del attrs["code"]
        return attrs

    class Meta:
        model = User
        fields = ("username", "code", "mobile", "password")
