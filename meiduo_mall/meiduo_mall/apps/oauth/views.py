# Create your views here.
import logging
import re

from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from oauth.models import OAuthQQUser
from oauth.utils import generate_access_token, check_access_token
from users.models import User

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

        # 使用openid判断该QQ用户是否绑定过美多商城的用户
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # openid未绑定用户
            access_token_openid = generate_access_token(openid)
            context = {'access_token_openid': access_token_openid}
            return render(request, 'oauth_callback.html', context)
        else:
            # openid已绑定用户
            login(request, oauth_user.user)
            # 重定向到state
            next = request.GET.get('state')
            response = redirect(next)
            # 为了实现首页右上角展示用户名信息
            response.set_cookie('username', oauth_user.user.username, max_age=3600 * 24 * 15)
            return response

    def post(self, request):
        """实现绑定用户的逻辑"""
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        access_token_openid = request.POST.get('access_token_openid')

        if not all([mobile, password, sms_code_client]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        if not re.match(r'^[0-9a-zA-Z_-]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断短信验证码是否一致
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # 判断openid是否有效
        openid = check_access_token(access_token_openid)
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': 'openid已失效'})

        # 使用手机号查询对应的用户是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 如果手机号用户不存在,新建用户
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        else:
            # 如果手机号用户存在,需要检验密码
            if not user.check_password(password):
                return render(request, 'oauth_callback.html', {'qq_login_errmsg': '账号或密码错误'})

        # 将新建用户(或已存在用户)绑定到openid
        try:
            # oauth_qq_user = OAuthQQUser(user=user,openid=openid)
            # oauth_qq_user.save()
            oauth_qq_user = OAuthQQUser.objects.create(user=user, openid=openid)
        except Exception as e:
            logger.error(e)
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': '账号或密码错误'})

        # 实现状态保持
        login(request, oauth_qq_user.user)

        # 重定向到state
        next = request.GET.get('state')
        response = redirect(next)

        # cookies中写入用户名
        response.set_cookie('username', oauth_qq_user.user.username, max_age=3600 * 24 * 15)

        return response


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
