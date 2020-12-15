from django.db import models


class BaseModel(models.Model):
    """为模型类补充字段"""
    # auto_now无论是你添加还是修改对象，时间为你添加或者修改的时间。
    # auto_now_add为添加时的时间，更新对象时不会有变动。
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True  # 说明是抽象模型类，用于继承使用，数据库迁移时不会创建BaseModel的表
