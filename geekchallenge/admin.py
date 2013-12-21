#-*- coding:utf-8 -*-
from geek.geekchallenge.models import *
from django.contrib import admin

class TeamAdmin(admin.ModelAdmin):
    '''
        后台显示团队
    '''
    list_display = ('user', 'team_score', 'answered_count')
admin.site.register(Team, TeamAdmin)


class ItemAdmin(admin.ModelAdmin):
    '''
        后台显示题目
    '''
    list_display = ('title', 'item_type', 'score', 'author', 'is_released', 'is_practice')
    list_filter = ['pub_time', 'item_type', 'score']
    search_fields = ['title', 'content']

    actions = ['set_release', 'set_practice_mode', 'cancel_release', 'cancel_practice_mode']

    def set_release(self, request, queryset):
        queryset.update(is_released=True)
    set_release.short_description = u"发放题目"

    def set_practice_mode(self, request, queryset):
        queryset.update(is_practice=True)
    set_practice_mode.short_description = u"设为练习模式"

    def cancel_practice_mode(self, request, queryset):
        queryset.update(is_practice=False)
    cancel_practice_mode.short_description = u"取消练习模式"

    def cancel_release(self, request, queryset):
        queryset.update(is_released=False)
    cancel_release.short_description = u"取消题目"

    class Media:
        js = [
            '/static/js/tiny_mce/tiny_mce_src.js',
            '/static/js/tiny_mce/tiny_mce_config.js',
        ]
admin.site.register(Item, ItemAdmin)


class ItemTypeAdmin(admin.ModelAdmin):
    '''
        后台显示题目分类
    '''
    list_display = ('type_name',)
admin.site.register(ItemType, ItemTypeAdmin)

class ItemAuthorAdmin(admin.ModelAdmin):
    '''
        后台显示题目作者
    '''
    list_display = ('author',)
admin.site.register(ItemAuthor, ItemAuthorAdmin)


class NoticesAdmin(admin.ModelAdmin):
    '''
        后台显示公告
    '''
    list_display = ('author', 'content',)
    class Media:
        js = [
            '/static/js/tiny_mce/tiny_mce_src.js',
            '/static/js/tiny_mce/tiny_mce_config.js',
        ]
admin.site.register(Notices, NoticesAdmin)

class RulesAdmin(admin.ModelAdmin):
    '''
        比赛规则
    '''
    class Media:
        js = [
            '/static/js/tiny_mce/tiny_mce_src.js',
            '/static/js/tiny_mce/tiny_mce_config.js',
        ]
admin.site.register(Rules, RulesAdmin)
