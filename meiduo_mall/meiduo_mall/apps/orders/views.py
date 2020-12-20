from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU
from users.models import Address

from decimal import Decimal


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """查询并展示要结算的订单数据"""
        user = request.user

        # 查询用户收货地址: 查询登录用户的没有被删除的收货地址
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except Exception as e:
            # 如果没有查询出地址, 可以去编辑收货地址
            addresses = None

        # 查询redis购物车中被勾选的商品
        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        redis_selected = redis_conn.smembers('selected_%s' % user.id)

        # 构造购物车中被勾选的商品数据
        new_cart_dict = {}
        for sku_id in redis_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

        # 获取被勾选的商品的sku_id
        sku_ids = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)

        total_count = 0
        total_amount = Decimal(0.00)
        # 遍历skus给每个sku补充count(数量)和amout(小计)
        for sku in skus:
            sku.count = new_cart_dict[sku.id]
            sku.amount = sku.price * sku.count

            total_count += sku.count
            total_amount += sku.amount

        # 指定默认的邮费
        freight = Decimal(10.00)

        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight,
        }

        return render(request, 'place_order.html', context)
