from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from user_operation.models import UserFav


# 收藏数+1
@receiver(post_save, sender=UserFav)
def create_userfav(sender, instance=None, created=False, **kwargs):
    # sender是用来接收哪个model传过来的，created会告诉是不是一个新建的，如果是新建的才修改，instance就是User
    if created:
        goods = instance.goods
        goods.fav_num += 1
        goods.save()


# 取消收藏
@receiver(post_delete, sender=UserFav)
def delete_userfav(sender, instance=None, created=False, **kwargs):
    # sender是用来接收哪个model传过来的，created会告诉是不是一个新建的，如果是新建的才修改，instance就是User
    goods = instance.goods
    goods.fav_num -= 1
    goods.save()
