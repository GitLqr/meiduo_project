# Create your views here.
import logging
import random

from django import http
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from verifications import constants
from verifications.libs.captcha.captcha import captcha
from verifications.libs.yuntongxun.ccp_sms import CCP

# 创建日志输出器
logger = logging.getLogger('django')


class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):
        """
        :param mobile: 手机号
        :return: JSON
        """
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 获取redis中的图形验证码
        redis_conn = get_redis_connection('verify_code')
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已失效'})
        # 删除redis中的图形验证码
        redis_conn.delete('img_%s' % uuid)

        # 对比图形验证码
        image_code_server = image_code_server.decode()  # 将bytes转字符串，再比较
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})

        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                constants.SEND_SMS_CODE_INTERVAL)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        """
        :param uuid: 通用唯一识别码，用于唯一标识该图形验证码属于哪个用户的
        :return: image/jpg
        """
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        return http.HttpResponse(image, content_type='image/jpg')
