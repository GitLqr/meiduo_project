# Create your views here.
from alipay import AliPay
from django import http
from django.conf import settings
from django.shortcuts import render
from django.views import View

from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from orders.models import OrderInfo
import os

from payment.models import Payment

app_private_key_string = open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/app_private_key.pem')).read()
alipay_public_key_string = open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/alipay_public_key.pem')).read()

# print(app_private_key_string)
# print(alipay_public_key_string)

alipay = AliPay(
    appid=settings.ALIPAY_APPID,
    app_notify_url=None,  # 默认回调url
    app_private_key_string=app_private_key_string,
    alipay_public_key_string=alipay_public_key_string,
    sign_type='RSA2',
    debug=settings.ALIPAY_DEBUG
)


class PaymentStatusView(LoginRequiredJSONMixin, View):
    """保存支付的订单状态"""

    def get(self, request):
        query_dict = request.GET
        # 将查询字符串参数的类型转成标准的字典类型
        data = query_dict.dict()

        # 从查询字符串参数中提取并移除 sign, 不能参与签名验证
        signature = data.pop('sign')

        # 使用SDK对象, 调用验证接口函数, 得到验证结果
        success = alipay.verify(data, signature)

        # 如果验证通过,需要将支付宝的支付状态进行处理(将美多商城的订单ID与支付宝的订单ID绑定, 修改订单状态)
        if success:
            # 美多商城维护的订单ID
            order_id = data.get('out_trade_no')
            # 支付宝维护的订单ID
            trade_id = data.get('trade_no')
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id,
            )
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
            context = {
                'trade_id': trade_id
            }
            return render(request, 'pay_success.html', context)
        else:
            return http.HttpResponseForbidden('非法请求')


class PaymentView(LoginRequiredJSONMixin, View):
    """对接支付宝的支付接口"""

    def get(self, request, order_id):
        """
        :param order_id: 当前要支付的订单ID
        :return:
        """
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject='美多商城%s' % order_id,
            return_url=settings.ALIPAY_RETURN_URL
        )

        # 拼接完整的支付宝登录页地址
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})
