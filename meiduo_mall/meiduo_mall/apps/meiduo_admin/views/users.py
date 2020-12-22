from rest_framework.generics import ListCreateAPIView

from meiduo_admin.serializers.users import UserSerializer
from meiduo_admin.utils import PageNum
from users.models import User


class UserView(ListCreateAPIView):
    """获取用户数据"""
    # queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNum

    def get_queryset(self):
        if self.request.query_params.get('keyword') == '':
            return User.objects.all()
        else:
            return User.objects.filter(username=self.request.query_params.get('keyword'))
