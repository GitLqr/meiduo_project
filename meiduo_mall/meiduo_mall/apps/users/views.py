import json
import logging
import re

from django import http
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from carts.utils import merge_cart_cookies_redis
from celery_tasks.email.tasks import send_verify_email
from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from users.models import User, Address
from users.utils import generate_verify_email_url, check_verify_email_token
from . import constants

logger = logging.getLogger('django')


class UserBrowseHistory(LoginRequiredJSONMixin, View):
    """用户浏览记录"""

    def post(self, request):
        """保存用户商品浏览记录"""
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        sku_id = json_dict.get('sku_id')

        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')

        redis_conn = get_redis_connection('history')
        user_history_key = 'history_%s' % request.user.id
        pl = redis_conn.pipeline()
        # 三步骤: 去重 保存(最新的在最前面) 截取(要求最多存5个)
        pl.lrem(user_history_key, 0, sku_id)
        pl.lpush(user_history_key, sku_id)
        pl.ltrim(user_history_key, 0, 4)
        pl.execute()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

    def get(self, request):
        """查询用户商品浏览记录"""
        redis_conn = get_redis_connection('history')
        user_history_key = 'history_%s' % request.user.id
        sku_ids = redis_conn.lrange(user_history_key, 0, -1)

        skus = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': skus})


class UpdateTitleAddressView(LoginRequiredJSONMixin, View):
    """更新地址标题"""

    def put(self, request, address_id):
        """实现更新更新地址标题逻辑"""
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        if not title:
            return http.HttpResponseForbidden('缺少title')

        try:
            address = Address.objects.get(id=address_id)
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新标题失败'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新标题成功'})


class DefaultAddressView(LoginRequiredJSONMixin, View):
    """设置默认地址"""

    def put(self, request, address_id):
        """实现设置默认地址逻辑"""
        try:
            address = Address.objects.get(id=address_id)
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})


class UpdateDestroyAddressView(LoginRequiredMixin, View):
    """更新或删除地址"""

    def put(self, request, address_id):
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # address = Address.objects.get(id=address_id)
        # address.title = ''
        # address.save()
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '修改地址失败'})

        address = Address.objects.get(id=address_id)
        address_dict = {
            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email
        }
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """删除地址"""
        # 实现指定地址的逻辑删除：is_deleted=True
        try:
            address = Address.objects.get(id=address_id)
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})


class AddressCreateView(LoginRequiredJSONMixin, View):
    """新增地址"""

    def post(self, request):
        """实现新增地址逻辑"""
        # 判断用户地址数量是否超过上限
        # count = Address.objects.filter(user=request.user).count()
        count = request.user.addresses.count()  # 一查多，使用related_name查询
        if count > constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超出用户地址上限'})

        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 保存用户传入的地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )
            # 如果登录用户没有默认的地址，我们需要指定默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失效'})

        address_dict = {
            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email
        }
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""

    def get(self, request):
        """查询并展示用户地址信息"""
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)
        address_list = []
        for address in addresses:
            address_dict = {
                'id': address.id,
                'title': address.title,
                'receiver': address.receiver,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'mobile': address.mobile,
                'tel': address.tel,
                'email': address.email
            }
            address_list.append(address_dict)
        context = {
            'default_address_id': login_user.default_address_id or '0',
            'addresses': address_list
        }
        return render(request, 'user_center_site.html', context)


class VerifyEmailView(View):
    """验证邮箱"""

    def get(self, request):
        token = request.GET.get('token')

        if not token:
            return http.HttpResponseForbidden('缺少token')

        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseBadRequest('无效的token')

        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮箱失败')

        return redirect(reverse('users:info'))


class EmailView(LoginRequiredJSONMixin, View):
    """添加邮箱"""

    def put(self, request):
        json_str = request.body.decode()  # body是bytes
        json_dict = json.loads(json_str)
        email = json_dict.get('email')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        # 发送邮箱验证邮件
        verify_url = generate_verify_email_url(request.user)
        send_verify_email.delay(email, verify_url)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""

    def get(self, request):
        """提供用户中心页面"""
        # 如果LoginRequiredMixin判断出用户已登录,那么request.user就是登录用户对象
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }
        return render(request, 'user_center_info.html', context)


class LogoutView(View):
    """用户退出登录"""

    def get(self, request):
        # 清除状态保持信息
        logout(request)
        # 退出登录后重定向到首页
        response = redirect(reverse('contents:index'))
        # 删除cookies中的用户名
        response.delete_cookie('username')
        return response


class LoginView(View):
    """用户登录"""

    def get(self, request):
        """提供用户登录页面"""
        return render(request, 'login.html')

    def post(self, request):
        """实现用户登录逻辑"""
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('密码最少8位,最长20位')

        # 认证用户
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '账号或密码错误'})

        # 状态保持
        login(request, user)
        if remembered != 'on':
            # 没有记住登录:状态保持在浏览器会话结束后就销毁
            request.session.set_expiry(0)  # 单位是秒
        else:
            # 记住登录:状态保持周期为两周(默认就是两周)
            request.session.set_expiry(None)

        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))

        # 为了实现首页右上角展示用户名信息
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        # 用户登录成功,合并cookie购物车到Redis购物车
        response = merge_cart_cookies_redis(request=request, user=user, response=response)

        return response


class MobileCountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """
        :param username: 用户名
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class RegisterView(View):
    """用户注册"""

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        """实现用户注册业务逻辑"""
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code_client = request.POST.get('sms_code')
        allow = request.POST.get('allow')

        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[a-zA-Z0-9-_]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password2):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')

        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码已失效'})
        if sms_code_client != sms_code_server.docode():
            return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})

        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')

        # return render(request, 'register.html', {'register_errmsg': '注册失败'})
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        login(request, user)

        response = redirect(reverse('contents:index'))
        # 为了实现首页右上角展示用户名信息
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response
