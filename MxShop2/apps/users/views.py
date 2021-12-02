from django.contrib.auth.backends import ModelBackend
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.mixins import CreateModelMixin
from rest_framework import viewsets
from .serializer import SmsSerializer, UserRegSerializer,UserDetailSerializer
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import status
from rest_framework import permissions
from rest_framework import authentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from utils.yunpian import Yunpian
from MxShop2.settings import API_KEY
from random import choice
from .models import VerifyCode
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

# Create your views here.
User = get_user_model()


class CustomBackend(ModelBackend):
    """
    自定义用户验证，如果要自定义用户验证就要继承ModelBackend，然后重写authenticate
    """

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            # 通过用户名和手机号验证，因为用户的个人中心的邮箱没有进行验证，有可能会重复的
            user = User.object.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeViewset(CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    serializer_class = SmsSerializer

    def generate_code(self):
        """
        生成四位数验证码
        """
        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))

        return "".join(random_str)

    # 重写CreateModelMixin的create方法
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 从序列化中取到mobile
        mobile = serializer.validated_data["mobile"]
        yun_pian = Yunpian(api_key=API_KEY)
        code = self.generate_code()
        sms_status = yun_pian.send_sms(code=code, mobile=mobile)
        print(sms_status)
        if sms_status["code"] != 0:
            # 如果验证失败，就返回400，状态码很重要
            return Response({
                "mobile": sms_status['code'],
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 短信发送成功，保存数据库
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                "mobile": mobile
            }, status.HTTP_201_CREATED)


class UserViewSet(CreateModelMixin,mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    用户
    """
    serializer_class = UserRegSerializer
    queryset = User.objects.all()
    authentication_classes = [authentication.SessionAuthentication,JSONWebTokenAuthentication]

    # 重载serializer这个函数，用来动态加载序列化
    def get_serializer_class(self):
        # 获取详细信息的时候
        if self.action == "retrieve":
            return UserDetailSerializer
        # 创建的时候
        elif self.action == "create":
            return UserRegSerializer
        # 一定要加一个默认返回的，否则会报错
        return UserDetailSerializer

    # permission_classes = [permissions.AllowAny,]
    # 重写get_permissions函数
    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return []
        # 一定要加一个默认返回的，否则会报错
        return []

    # 重载CreateModelMixin的create函数和perform_create函数
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 拿到User，就可以生成对应的JWT的token
        # 要跟踪源码分析哪个函数生成的token，这个比较关键，在后期第三方登陆的时候也要用到这个逻辑
        user = self.perform_create(serializer)

        # 因为返回的是serializer.data，所以先把data取出来
        re_dict = serializer.data

        # 生成JTWtoken需要的payload
        payload = jwt_payload_handler(user)
        # 生成token，因为前端也叫token
        re_dict["token"] = jwt_encode_handler(payload)
        # 比如想添加一个name，因为前端还有一个name
        re_dict["name"] = user.name if user.name else user.username
        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    # 重写get_object方法，获取用户ID
    def get_object(self):
        # 直接返回user
        return self.request.user

    # 因为要生成token的时候必须要先拿到user，perform_create只是调用了save函数，并没有返回，要重载这个函数，将user返回
    def perform_create(self, serializer):
        return serializer.save()
