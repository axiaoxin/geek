#!/usr/bin/env python
#-*- coding:utf-8 -*-
__author__ = 'AshIn'

from django.forms import ModelForm
from geek.geekchallenge.models import *
from django import forms
from django.contrib.auth.models import User

institute_choices = [
            (u'网络工程学院', u'网络工程学院'), (u'软件工程学院', u'软件工程学院'), (u'计算机学院', u'计算机学院'), 
            (u'大气科学学院', u'大气科学学院'), (u'电子工程学院', u'电子工程学院'), (u'控制工程学院', u'控制工程学院'),
            (u'管理学院', u'管理学院'), (u'光电技术学院', u'光电技术学院'), (u'政治学院', u'政治学院'),
            (u'统计学院', u'统计学院'), (u'软件与服务外包学院', u'软件与服务外包学院'), (u'银杏学院', u'银杏学院'),
            (u'资源环境学院', u'资源环境学院'), (u'通信工程学院', u'通信工程学院'), (u'数学学院', u'数学学院'),
            (u'外国语学院', u'外国语学院'), (u'文化艺术学院', u'文化艺术学院'), (u'商学院', u'商学院'),
            (u'继续教育学院', u'继续教育学院'), (u'网络商学院', u'网络商学院'), (u'校外团队', u'校外团队'),
        ]

class RegisterForm(forms.Form):
    '''
        注册表单
    '''
    team_name = forms.CharField(label=u'团队名称', max_length=20, required=True)
    password1 = forms.CharField(label=u'登录密码', min_length=6, max_length=16, required=True, widget=forms.PasswordInput())
    password2 = forms.CharField(label=u'确认密码', min_length=6, max_length=16, required=True, widget=forms.PasswordInput())
    team_email = forms.EmailField(label=u'联系邮箱', required=True)
    leader_name = forms.CharField(label=u'队长名字', max_length=10, required=True)
    leader_number = forms.CharField(label=u'队长学号', max_length=10, required=True)
    institute = forms.ChoiceField(label=u'所属学院', choices=institute_choices)
    team_member = forms.CharField(label=u'团队成员', max_length=30, required=True)
    motto = forms.CharField(label=u'参赛口号', max_length=50, required=True)
    
    p1 = p2 = ''

    def clean_password1(self):
        '''
            验证密码1长度
        '''
        self.p1 = self.cleaned_data.get('password1')
        if not 6 <= len(self.p1) <= 16:
            raise forms.ValidationError(u'密码长度应为6-16个字符！')
        return self.p1

    def clean_password2(self):
        '''
            验证密码2是否与密码1相同
        '''
        self.p2 = self.cleaned_data.get('password2')
        if self.p1 != self.p2:
            raise forms.ValidationError(u'密码不一致！')
        return self.p1

    def clean_team_name(self):
        '''
            验证用户名是否已被注册
        '''
        username = self.cleaned_data['team_name']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(u'该用户名已被注册！')

    def clean_leader_number(self):
        '''
            验证学号，20xxxxxxxx，10位
        '''
        number = self.cleaned_data['leader_number']
        from re import match
        if len(number) != 10 or not match('20\d{8}', number):
            raise forms.ValidationError(u'请输入以20开头的10位数学号！')
        return number

class LoginForm(forms.Form):
    '''
        登录表单
    '''
    team_name = forms.CharField(label=u'团队名称', max_length=20, required=True)
    password = forms.CharField(label=u'登录密码', min_length=6, max_length=16, required=True, widget=forms.PasswordInput())

    def clean_team_name(self):
        '''
            验证用户名是否正确
        '''
        username = self.cleaned_data['team_name']
        try:
            User.objects.get(username=username)
            return username
        except User.DoesNotExist:
            raise forms.ValidationError(u'该用户名错误！')

class TeamInfoForm(forms.Form):
    '''
        团队信息表单
    '''
    leader_name = forms.CharField(label=u'队长姓名', max_length=10, required=True)
    leader_number = forms.CharField(label=u'队长学号', max_length=10, required=True)
    institute = forms.ChoiceField(label=u'所属学院', choices=institute_choices, required=True)
    team_member = forms.CharField(label=u'团队成员', max_length=30, required=True)
    motto = forms.CharField(label=u'参赛口号', max_length=50, required=True)

    def clean_leader_number(self):
        number = self.cleaned_data['leader_number']
        from re import match
        if len(number) != 10 or not match('20\d{8}', number):
            raise forms.ValidationError(u'请输入以20开头的10位数学号！')
        return number

class ChangePasswordForm(forms.Form):
    '''
        修改密码表单
    '''
    old_password = forms.CharField(label=u'当前密码', widget=forms.PasswordInput(), required=True, min_length=6, max_length=16)
    password1 = forms.CharField(label=u'新的密码', widget=forms.PasswordInput(), max_length=16, min_length=6, required=True)
    password2 = forms.CharField(label=u'确认密码', widget=forms.PasswordInput(), max_length=16, required=True, min_length=6)

    p1 = p2 = ''
    def clean_password1(self):
        '''
            验证密码1长度
        '''
        self.p1 = self.cleaned_data.get('password1')
        if not 6 <= len(self.p1) <= 16:
            raise forms.ValidationError(u'密码长度应为6-16个字符！')
        return self.p1

    def clean_password2(self):
        '''
            验证密码2是否等于密码1
        '''
        self.p2 = self.cleaned_data.get('password2')
        if self.p1 != self.p2:
            raise forms.ValidationError(u'密码不一致！')
        return self.p1


class ForgetPasswordForm(forms.Form):
    """
        忘记密码，注册信息表单
    """
    username = forms.CharField(label=u'团队名称', max_length=20, required=True)
    email = forms.EmailField(label=u'注册邮箱', required=True)
    
    def clean_username(self):
        '''
            验证用户名是否存在
        '''
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
            return username
        except User.DoesNotExist:
            raise forms.ValidationError(u'团队名称不存在！')

class ResetPasswordForm(forms.Form):
    """
        忘记密码，重置密码表单
    """
    password1 = forms.CharField(label=u'新的密码', widget=forms.PasswordInput(), max_length=16, min_length=6, required=True)
    password2 = forms.CharField(label=u'确认密码', widget=forms.PasswordInput(), max_length=16, required=True, min_length=6)

    p1 = p2 = ''
    def clean_password1(self):
        '''
            验证密码1长度
        '''
        self.p1 = self.cleaned_data.get('password1')
        if not 6 <= len(self.p1) <= 16:
            raise forms.ValidationError(u'密码长度应为6-16个字符！')
        return self.p1

    def clean_password2(self):
        '''
            验证密码2是否等于密码1
        '''
        self.p2 = self.cleaned_data.get('password2')
        if self.p1 != self.p2:
            raise forms.ValidationError(u'密码不一致！')
        return self.p1
