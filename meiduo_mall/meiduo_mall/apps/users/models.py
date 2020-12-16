from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    """自定义用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')  # 追加字段最好填写默认值

    class Meta:
        db_table = 'tb_users'  # 自定义表名
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
