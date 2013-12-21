#-*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
import datetime
from geek.geekchallenge.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import re

class Area(models.Model):
    """论坛分区"""
    area_name = models.CharField(verbose_name=u"分区名称", max_length=10)
    desc = models.CharField(verbose_name=u"分区简介", max_length=50, blank=True, null=True)

    def __unicode__(self):
        return self.area_name

    class Meta:
        verbose_name_plural = u"论坛分区"


class Forum(models.Model):
    """分区版块"""
    name = models.CharField(verbose_name=u"版块名称", max_length=10)
    area = models.ForeignKey(Area, verbose_name=u"所属分区")
    parent = models.ForeignKey('self', verbose_name=u"上级版块", blank=True, null=True, related_name="child")
    desc = models.CharField(verbose_name=u"版块简介", max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = u"分区版块"

    def __unicode__(self):
        return self.name

    def latest_thread(self):
        """版块最新帖子"""
        try:
            self.__latest_thread = Thread.objects.filter(forum=self).latest("submit_time")
        except Exception, e:
            self.__latest_thread = None
        return self.__latest_thread

    def thread_count(self):
        self.__thread_count = Thread.objects.filter(forum=self).count()
        return self.__thread_count
    thread_count.short_description = u"帖子总数"

    def reply_count(self):
        self.__reply_count = Reply.objects.filter(thread__forum=self).count()
        return self.__reply_count
    reply_count.short_description = u"回复总数"
        

class Thread(models.Model):
    forum = models.ForeignKey(Forum, verbose_name=u"所属版块")
    author = models.ForeignKey(Team, verbose_name=u"帖子作者")
    title = models.CharField(verbose_name=u"帖子标题", max_length=35)
    content = models.TextField(verbose_name=u"帖子内容")
    submit_time = models.DateTimeField(verbose_name=u"发表时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=u"更新时间", blank=True, null=True, editable=False)
    clicked = models.IntegerField(verbose_name=u"点击量", default=0, editable=False)
    is_toped = models.BooleanField(verbose_name=u"置顶", blank=True, default=False)
    is_elite = models.BooleanField(verbose_name=u"精华", blank=True, default=False)

    def reply_count(self):
        self.__reply_count = Reply.objects.filter(thread=self).count()
        return self.__reply_count
    reply_count.short_description = u"回复数"

    def latest_reply(self):
        self.__latest_reply = Reply.objects.filter(thread=self).latest('submit_time')
        return self.__latest_reply

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name_plural = u"版块帖子"
        ordering = ['-submit_time']
    
class Reply(models.Model):
    thread = models.ForeignKey(Thread, verbose_name=u"所属帖子")
    author = models.ForeignKey(Team, verbose_name=u"回复作者")
    content = models.TextField(verbose_name=u"回复内容")
    submit_time = models.DateTimeField(verbose_name=u"发表时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=u"更新时间", blank=True, null=True, editable=False)

    events = generic.GenericRelation('Event')

    def __unicode__(self):
        return self.submit_time.strftime("%Y-%m-%d %H:%m:%S")

    class Meta:
        verbose_name_plural = u"帖子回复"

@receiver(post_save, sender=Reply, dispatch_uid="ashin_unique_identifier")
def post_save_handler(sender, instance, **kwargs):
    reply = instance
    team_name_pattern = re.compile('(?<=@)(\w+)', re.UNICODE)
    at_team_names = set(re.findall(team_name_pattern, reply.content))
    if at_team_names:
        for at_team_name in at_team_names: 
            if at_team_name != reply.author.user.username:
                try:
                    at_team = User.objects.get(username=at_team_name)
                    event = Event(author=reply.author.user, event=reply, at_team=at_team)
                    event.save()
                except:
                    pass
    elif reply.author != reply.thread.author:
        event = Event(author=reply.author.user, event=reply, at_team=reply.thread.author.user)
        event.save()


class Event(models.Model):
    content_type = models.ForeignKey(ContentType, verbose_name=u"被触发的模型")
    object_id = models.PositiveIntegerField(verbose_name=u"被触发模型ID")

    author = models.ForeignKey(User, verbose_name=u"事件发起者", related_name="author")
    event = generic.GenericForeignKey('content_type', 'object_id')
    at_team = models.ForeignKey(User, verbose_name=u"提到的人", related_name="at_team")
    #两个外键都指向User必须使用related_name参数
    submit_time = models.DateTimeField(verbose_name=u"@时间", auto_now_add=True)
    is_readed = models.BooleanField(verbose_name=u"已读", default=False, editable=False)
    is_deleted = models.BooleanField(verbose_name=u"已被删除", default=False, editable=False)


    def __unicode__(self):
        return u"%s在回复%s的帖子《%s》中提到了%s"%(self.author, self.event.thread.author, self.event.thread, self.at_team)

    class Meta:
        verbose_name_plural = u"回复新闻"
        ordering = ["-submit_time"]


class SensitiveWords(models.Model):
    words = models.CharField(verbose_name=u"敏感词汇", max_length=10)
    submit_time = models.DateTimeField(verbose_name=u"添加时间", auto_now_add=True)
    
    def __unicode__(self):
        return self.words

    class Meta:
        verbose_name_plural = u"敏感词汇"
