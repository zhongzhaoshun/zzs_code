from django.contrib.auth.backends import ModelBackend
from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.mixins import CreateModelMixin
from rest_framework import viewsets
from .serializers import SmsSerializer, UserRegSerializer
from MxShop.settings import APIKEY

User = get_user_model()
from rest_framework.response import Response
from rest_framework import status
from utils.yunpian import YunPian
from random import choice
from .models import VerifyCode

from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler


# 自定义验证一定要继承ModelBackend，重写authenticate
class CustomBackend(ModelBackend):
    """自定义用户验证"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


# 验证码
class SmsCodeViewset(CreateModelMixin, viewsets.GenericViewSet):
    "发送验证码"
    serializer_class = SmsSerializer

    # 生成四位数验证码
    def generate_code(self):
        seeds = "1234567890"
        random_str = []
        for i in range(4):
            # 在字符串中随机取一位
            random_str.append(choice(seeds))

        return "".join(random_str)

    # 重写CreateModelMixin的create
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # raise_exception如果为True,如果is_valid调用失败就回抛异常，可以保持不变
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data['mobile']
        yunpian = YunPian(APIKEY)
        # 发送短信
        code = self.generate_code()
        sms_status = yunpian.send_sms(code=code, mobile=mobile)
        """
        名称	    类型	    描述
        code	    integer	    0 代表发送成功，其他 code 代表出错，详细见"返回值说明"页面
        msg	        text	    例如""发送成功""，或者相应错误信息
        count	    integer	    发送成功短信的计费条数(计费条数：70 个字一条，超出 70 个字时按每 67 字一条计费)
        fee	        double	    扣费金额，单位：元，类型：双精度浮点型/double
        unit	    string	    计费单位；例如：“RMB”
        mobile	    string	    发送手机号
        sid	        long(64位)	短信 id，64 位整型， 对应 Java 和 C#的 long，不可用 int 解析
        """
        # 返回值不等于0，发送失败
        if sms_status["code"] != 0:
            return Response({
                "mobile": sms_status["msg"]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 发送成功,保存数据库
            code_recode = VerifyCode(code=code, mobile=mobile)
            code_recode.save()
            return Response({
                "mobile": mobile
            }, status=status.HTTP_201_CREATED)


class UserViewset(CreateModelMixin, viewsets.GenericViewSet):
    "用户"
    serializer_class = UserRegSerializer
    queryset = User.objects.all()

    # 重载create函数，前端传递过来了一个token
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.perform_create(serializer)
        payload = jwt_payload_handler(user)
        re_dict = serializer.data
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["name"] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    # 返回的是serializer_class里的meta里的model对象
    def perform_create(self, serializer):
        return serializer.save()
