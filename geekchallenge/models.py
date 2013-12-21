#-*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import *
from geek.geekchallenge.utils import *
from geek import settings

class Team(models.Model):
    '''
        团队信息，一对一关联User
    '''
    user = models.ForeignKey(User,verbose_name=u'团队名称')
    leader_name = models.CharField(verbose_name=u'队长名字', max_length=10)
    leader_number = models.CharField(verbose_name=u'队长学号', max_length=10)
    institute = models.CharField(verbose_name=u'所属学院', max_length=10)
    team_score = models.IntegerField(verbose_name=u'团队总分', default=0, editable=False) #得分设置为不可编辑（后台表单不显示）
    answered_count = models.IntegerField(verbose_name=u'答对题数', default=0, editable=False)
    team_member = models.CharField(u'团队成员', max_length=20)
    last_submit_time = models.DateTimeField(verbose_name=u'提交时间', auto_now_add=True) #auto_now每次有提交后都会更新时间,auto_now_add只记录第一次
    motto = models.CharField(verbose_name=u'团队口号', max_length=40)
    activation_code = models.CharField(max_length=40, verbose_name=u'激活码')
    code_expires = models.DateTimeField(verbose_name=u'激活期限')
    reset_password_code = models.CharField(max_length=40, null=True, blank=True, verbose_name=u'重置码')
    reset_expires = models.DateTimeField(null=True, blank=True, verbose_name=u'重置期限')


    def __unicode__(self):
        return self.user.username

    class Meta:
        ordering = ['-team_score', 'answered_count', 'last_submit_time']
        verbose_name_plural = u'团队信息'

class ItemType(models.Model):
    '''
        题目分类
    '''
    type_name = models.CharField(verbose_name=u'分类名称', max_length=8, unique=True)
    type_img = models.ImageField(verbose_name=u'标志图片', upload_to='imgs/')
    type_desc = models.CharField(verbose_name=u'分类描述', max_length=50, blank=True)
    
    def __unicode__(self):
        return self.type_name

    def save(self):
        '''
            重写save方法，保存后对图片进行相应的处理
        '''
        super(ItemType, self).save()
        img_path = '%s/%s'%(settings.MEDIA_ROOT, self.type_img.name)
        new_img = deal_img(img_path) #处理图片
        new_img.save(img_path)

    class Meta:
        ordering = ['id']
        verbose_name_plural = u'题目分类'
    
class ItemAuthor(models.Model):
    '''
        题目作者
    '''
    author = models.CharField(verbose_name=u'题目作者', max_length=20)
    
    def __unicode__(self):
        return self.author

    class Meta:
        ordering = ['id']
        verbose_name_plural = u'题目作者'

class Item(models.Model):
    '''
        比赛题目
    '''
    item_type = models.ForeignKey(ItemType, verbose_name=u'题目分类')
    title = models.CharField(verbose_name=u'题目标题', max_length=50, unique=True)
    content = models.TextField(verbose_name=u'题目描述')
    attachment = models.FileField(verbose_name=u'题目附件', upload_to='attachments/', null=True, blank=True, help_text=u'请上传打包后的文件，以便用户点击就能下载')
    pub_time = models.DateTimeField(verbose_name=u'发布时间', auto_now_add=True)
    score = models.IntegerField(verbose_name=u'题目分值')
    author = models.ForeignKey(ItemAuthor, verbose_name=u'题目作者')
    answer = models.CharField(verbose_name=u'题目答案', max_length=100, )#help_text=u'若点击保存，务必都要将答案改为正确的明文答案后再保存，因为答案已被加密')
    answered_by_team = models.ManyToManyField(Team, editable=False, null=True, blank=True)
    is_released = models.BooleanField(verbose_name=u"发放题目", default=False)
    is_practice = models.BooleanField(verbose_name=u"练习模式", default=False)

    def __unicode__(self):
        return self.title

    def save(self):
        #self.answer = hash_answer(self.answer)
        super(Item, self).save()


    class Meta:
        ordering = ['item_type', 'score', 'id']
        verbose_name_plural = u'比赛题目'


class Notices(models.Model):
    content = models.TextField(verbose_name=u'公告内容')
    author = models.ForeignKey(ItemAuthor, verbose_name=u'公告作者')
    pub_time = models.DateTimeField(verbose_name=u'发布时间', auto_now=True)

    class Meta:
        ordering = ['-pub_time']
        verbose_name_plural = u'比赛公告'

class Rules(models.Model):
    content = models.TextField(verbose_name=u'公告内容')
    pub_time = models.DateTimeField(verbose_name=u'发布时间', auto_now=True)

    class Meta:
        verbose_name_plural = u'比赛规则'
