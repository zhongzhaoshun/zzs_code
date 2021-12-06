from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from .models import UserFav, UserLeavingMessage, UserAddress
from .serializer import UserFavSerializer, UserFavDetailSerializer, LeavingMessageSealizer, AddessSerializer
from rest_framework.permissions import IsAuthenticated
from utils.permissions import IsOwnerOrReadOnly
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response


# Create your views here.


# 用户收藏功能
# 可以把收藏看做为写入一条数据，取消收藏看做删除
# 获取收藏商品用到了mixins.ListModelMixin，添加收藏用到了mixins.CreateModelMixin，取消收藏用到了mixins.DestroyModelMixin
class UserFavViewset(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    list:
        获取用户收藏列表
    retrive:
        判断某个商品是否已经收藏
    create:
        收藏商品
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    # queryset = UserFav.objects.all()
    serializer_class = UserFavSerializer
    # 将JSONWebTokenAuthentication配置到views，之前在goods的views里也配置过，这样就不会全局验证过jsontoken了
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    lookup_field = "goods_id"



    # 重载serializer这个函数，用来动态加载序列化
    def get_serializer_class(self):
        # 获取详细信息的时候
        if self.action == "list":
            return UserFavDetailSerializer
        # 创建的时候
        elif self.action == "create":
            return UserFavSerializer
        # 一定要加一个默认返回的，否则会报错
        return UserFavSerializer

    def get_queryset(self):
        return UserFav.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# 用户留言功能
class LeavingMessageViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """
    用户留言
    list:
        获取用户留言
    create：
        添加留言
    delete：
        删除留言
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    serializer_class = LeavingMessageSealizer

    # 只返回当前用户的留言
    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)


class AddressViewSet(viewsets.ModelViewSet):
    """
    收货地址管理
    list:
        获取收货地址
    create:
        添加收货地址
    update:
        更新收货地址
    delete：
        删除收货地址
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    serializer_class = AddessSerializer

    # 只返回当前用户的地址
    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)
