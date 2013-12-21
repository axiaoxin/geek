#!/usr/bin/env python
#-*- coding:utf-8 -*-
__author__ = 'AshIn'

from geek.geekchallenge.models import *
from django import forms
from django.contrib.auth.models import User


class NewThreadForm(forms.Form):
    '''
        发帖表单
    '''
    title = forms.CharField(label=u'帖子标题(必填，不得超过35字)', max_length=35, required=True, widget=forms.TextInput({'style':'width:100%'}))
    content = forms.CharField(label=u'帖子内容(必填)', required=True, widget=forms.Textarea({'style':'width:100%'}))

class ReplyForm(forms.Form):
    '''
        回复表单
    '''
    content = forms.CharField(label=u'回复内容(必填)', required=True, widget=forms.Textarea({'style':'width:100%'}))

   
