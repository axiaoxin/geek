#-*- coding:utf-8 -*-
from geek.forum.models import *
from django.contrib import admin

class AreaAdmin(admin.ModelAdmin):
    '''
        显示分区
    '''
    list_display = ('area_name', 'desc')
admin.site.register(Area, AreaAdmin)

class ForumAdmin(admin.ModelAdmin):
    '''
        显示版块
    '''
    list_display = ('name', 'desc', 'area', 'parent', 'thread_count', 'reply_count')
admin.site.register(Forum, ForumAdmin)

class ThreadAdmin(admin.ModelAdmin):
    '''
        显示帖子
    '''
    list_display = ('title', 'forum', 'author', 'submit_time', 'clicked', 'reply_count', 'is_toped', 'is_elite')
    search_fileds = ['title', 'author']
    list_filter = ['submit_time', 'is_toped', 'is_elite']
    actions = ['set_elite', 'cancel_elite', 'set_top', 'cancel_top']

    def set_elite(self, request, queryset):
        queryset.update(is_elite=True)
    set_elite.short_description = u"设为精华帖"

    def cancel_elite(self, request, queryset):
        queryset.update(is_elite=False)
    cancel_elite.short_description = u"取消精华帖"

    def set_top(self, request, queryset):
        queryset.update(is_toped=True)
    set_top.short_description = u"设为置顶"

    def cancel_top(self, request, queryset):
        queryset.update(is_toped=False)
    cancel_top.short_description = u"取消置顶"
admin.site.register(Thread, ThreadAdmin)

class ReplyAdmin(admin.ModelAdmin):
    '''
        显示帖子
    '''
    list_display = ('thread', 'author', 'submit_time')
admin.site.register(Reply, ReplyAdmin)

class SensitiveWordsAdmin(admin.ModelAdmin):
    '''
        显示敏感词汇
    '''
    list_display = ('words', 'submit_time')
admin.site.register(SensitiveWords, SensitiveWordsAdmin)

admin.site.register(Event)
