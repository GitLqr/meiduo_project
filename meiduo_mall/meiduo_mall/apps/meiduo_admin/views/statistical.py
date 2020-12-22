from datetime import date, timedelta
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import GoodsVisitCount
from meiduo_admin.serializers.statistical import UserGoodsCountSerializer
from users.models import User


class UserCountView(APIView):
    """
    用户总量统计
    """
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        count = User.objects.all().count()
        return Response({
            'date': now_date,
            'count': count
        })


class UserDayCountView(APIView):
    """
    日增用户统计
    """
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        count = User.objects.filter(date_joined__gte=now_date).count()
        return Response({
            'date': now_date,
            'count': count
        })


class UserDayActiveCountView(APIView):
    """
    日活用户统计
    """
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        count = User.objects.filter(last_login__gte=now_date).count()
        return Response({
            'date': now_date,
            'count': count
        })


class UserDayOrdersCountView(APIView):
    """
    下单用户统计
    """
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        count = len(set(User.objects.filter(orders__create_time__gte=now_date)))
        return Response({
            'date': now_date,
            'count': count
        })


class UserMonthCountView(APIView):
    """
    月增用户统计
    """
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        begin_date = now_date - timedelta(days=29)
        data_list = []
        for i in range(30):
            # 起始日期
            index_date = begin_date + timedelta(days=i)
            # 第二天的日期
            next_date = begin_date + timedelta(days=i + 1)
            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=next_date).count()
            data_list.append({
                'count': count,
                'date': index_date
            })
        return Response(data_list)


class UserGoodsCountView(APIView):
    """
    日分类商品访问量统计
    """
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        goods = GoodsVisitCount.objects.filter(date__gte=now_date)
        ser = UserGoodsCountSerializer(goods, many=True)
        return Response(ser.data)
