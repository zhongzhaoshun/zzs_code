from rest_framework import serializers
from .models import UserFav
from rest_framework.validators import UniqueTogetherValidator
from goods.serializers import GoodsSerializer
from .models import UserLeavingMessage, UserAddress


class UserFavDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer()

    class Meta:
        model = UserFav
        fields = ['goods', "id"]


class UserFavSerializer(serializers.ModelSerializer):
    # 获取当前登陆的用户
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserFav
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=['user', 'goods'],
                message="已经收藏"
            )
        ]

        # 需要取消收藏，就是删除数据的时候，就要将ID返回回来
        fields = ['user', 'goods', "id"]


class LeavingMessageSealizer(serializers.ModelSerializer):
    # 获取当前登陆的用户
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    class Meta:
        model = UserLeavingMessage
        # 因为删除留言的时候要根据ID删除
        fields = ['user', 'msg_type', "subject", 'message', 'file', 'id', "add_time"]


class AddessSerializer(serializers.ModelSerializer):
    # 获取当前登陆的用户
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    class Meta:
        model = UserAddress
        fields = ["id", 'user', 'province', "city", 'district', 'address', 'signer_name', "signer_mobile", "add_time"]
