from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    # sender是用来接收哪个model传过来的，created会告诉是不是一个新建的，如果是新建的才修改，instance就是User
    if created:
        password = instance.password
        instance.set_password(password)
        instance.save()
