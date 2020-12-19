from django.core.files.storage import Storage
from django.conf import settings

import global_config


class FastDFSStorage(Storage):
    """自定义文件存储类"""

    def __init__(self, fdfs_base_url=None):
        """文件存储类的初始化方法"""
        self.fdfs_base_url = fdfs_base_url or global_config.FDFS_URL_PREFIX

    def _open(self, name, mode='rb'):
        """
        打开文件时会被调用的: 文档告诉我必须重写
        :param name: 文件路径
        :param mode: 文件打开方式
        :return: None
        """
        # 因为当前不是去打开某个文件,所以这个方法目前无用,但是又必须重写,所以pass
        pass

    def _save(self, name, content):
        """
        保存文件时会被调用的: 文档告诉我必须重写
        PS:将来后台管理系统中,需要在这个方法中实现文件上传到FastDFS服务器
        :param name: 文件路径
        :param content: 文件二进制内容
        :return:None
        """
        # 因为当前不是去保存文件,所以这个方法目前无用,但是又必须重写,所以pass
        pass

    def url(self, name):
        """
        返回文件的全路径
        :param name: 文件相对路径
        :return: 文件的全路径
        """
        return self.fdfs_base_url + name
