# -*- encoding: utf-8 -*-
'''
@File    :   signals.py   
@Contact :   nick623738321@163.com
@Author  :    zzs
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/9/11 22:12   zzs         1.0          None
'''

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


# sender监听User的传递
@receiver(post_save, sender=User)
# created监听是否是新建的，如果是新建的才进行修改
# user.model继承了AbstractUser，AbstractUser里的AbstractUser有set_password
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        password = instance.password
        instance.set_password(password)
        instance.save()
