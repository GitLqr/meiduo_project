from django.db import DatabaseError
from django.shortcuts import render, redirect
from django import http
# Create your views here.
from django.urls import reverse
from django.views import View
import re

from users.models import User


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
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')

        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        # return http.HttpResponse('注册成功, 重定向到首页')
        # return redirect('/')
        return redirect(reverse('contents:index'))
