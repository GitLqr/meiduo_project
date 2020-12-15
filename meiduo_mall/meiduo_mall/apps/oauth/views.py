# Create your views here.
from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.conf import settings
from django.views import View

from meiduo_mall.utils.response_code import RETCODE
import logging

logger = logging.getLogger('django')


class QQAuthUserView(View):
    """处理QQ登录回调"""

    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('获取code失败')
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 使用code获取access_token
            access_token = oauth.get_access_token(code)
            # 使用access_token获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')


class QQAuthURLView(View):
    """
    提供QQ登录扫码页面
    QQ互联的回调地址是www.meiduo.site，所以需要修改本机host，指定www.meiduo.site到127.0.0.1
    """

    def get(self, request):
        next = request.GET.get('next')
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        # 生成qq登录扫码链接地址
        login_url = oauth.get_qq_url()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})
