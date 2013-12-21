#-*- coding:utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from geek.geekchallenge.forms import *
from geek.geekchallenge.models import *
from geek.geekchallenge.utils import *
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import *
import datetime, random, hashlib
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
from geek import settings 
import logging, threading
log = logging.getLogger(__name__)

def home(request):
    '''
        主页视图，显示最新一条公告
    '''
    latest_notices = None
    try:
        latest_notices = Notices.objects.latest("id")
    except:
        pass

    return render_to_response('home.html', {'latest_notices':latest_notices}, context_instance=RequestContext(request))

def team_login(request):
    '''
        登录视图
    '''
    form = LoginForm()
    if request.method == 'GET':
        if request.META.get('HTTP_REFERER', '/').endswith('/accounts/login/'):
            request.session['login_from'] = '/notices/'
        else:
            request.session['login_from'] = request.META.get('HTTP_REFERER', '/') #将登录前用户说在页面存入session
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['team_name'], password=cd['password'])
            if user is not None and user.is_active:
                login(request, user)
                messages.add_message(request, messages.INFO, u'登录成功，欢迎回来！')
                #return HttpResponseRedirect(reverse('geek.geekchallenge.views.home', args=())) #登陆后跳转到首页
                return HttpResponseRedirect(request.session['login_from']) #登录后跳转到登陆前所在页面
            else:
                messages.add_message(request, messages.INFO, u'密码错误或帐号尚未激活')
    return render_to_response('login.html', {'form':form,}, context_instance=RequestContext(request))

def team_logout(request):
    '''
        退出登录
    '''
    if request.user.is_authenticated():
        logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    #return HttpResponseRedirect(reverse('geek.geekchallenge.views.home', args=()))

def register(request):
    '''
        用户注册视图
    '''
    form = RegisterForm(initial={'leader_number':u'校外团队填20开头的任意10位数字'})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.create_user(username=cd['team_name'], email=cd['team_email'], password=cd['password1'])
            user.is_active = False
            user.save()
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            activation_code = hashlib.sha1(salt + user.username.encode('utf-8')).hexdigest()
            code_expires = datetime.datetime.today() + datetime.timedelta(days=1)
            team = Team(user=user, leader_name=cd['leader_name'], leader_number=cd['leader_number'], institute=cd['institute'], team_member=cd['team_member'], motto=cd['motto'], activation_code=activation_code, code_expires=code_expires)
            team.save()
            #发送验证邮件

            def mail_thread():
                try:
                    subject = u"成都信息工程学院%s在线答题平台帐号激活邮件"%settings.PLATFORM_MODE
                    body = u"你好，%s团队：\n\n感谢注册成都信息工程学院%s在线答题平台帐号，登录平台必须激活帐号。\n请务必在24小时内点击 http://%s/accounts/confirm/%s/ 激活您的团队帐号。\n过期失效，需重新注册。\n\nby Syclover-阿小信"%(user.username, settings.PLATFORM_MODE, settings.PLATFORM_HOST, team.activation_code)
                    send_mail(subject, body, settings.EMAIL_HOST_USER, [user.email])
                except Exception, e:
                    log.debug(u'注册邮件发送失败, %s, To:%s'%(str(e), user.email))

            threading.Thread(target=mail_thread, args=()).start()
            messages.add_message(request, messages.INFO, u'请查看你的注册邮箱,激活你的团队帐号后才能登录答题平台！')
            return HttpResponseRedirect(reverse('geek.geekchallenge.views.team_login', args=()))

    return render_to_response('register.html', {'form':form, }, context_instance=RequestContext(request))

def confirm(request, activation_code):
    team = get_object_or_404(Team, activation_code=activation_code)
    if team.code_expires < datetime.datetime.today() and not team.user.is_active:
        messages.add_message(request, messages.INFO, u'激活帐号时间期限已过，请重新注册！')
        dead_man = User.objects.get(username = team.user)
        dead_man.delete()
        return HttpResponseRedirect(reverse('geek.geekchallenge.views.team_login', args=()))
    elif team.user.is_active or request.user.is_active:
        messages.add_message(request, messages.INFO, u'已激活帐号，无需再次激活！')
        return HttpResponseRedirect(reverse('geek.geekchallenge.views.team_login', args=()))

    user = team.user
    user.is_active = True
    user.save()
    messages.add_message(request, messages.INFO, u'成功激活帐号，欢迎回来！')
    #激活后跳转到登录页面
    return HttpResponseRedirect(reverse('geek.geekchallenge.views.team_login', args=()))

def forget_password(request):
    '''
        用户忘记密码
    '''
    form = ForgetPasswordForm()
    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = get_object_or_404(User, username=cd['username'])
            if user.email == cd['email']:
                salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
                reset_password_code = hashlib.sha1(salt + user.username.encode('utf-8')).hexdigest()
                reset_expires = datetime.datetime.today() + datetime.timedelta(days=1)
                team = get_object_or_404(Team, user=user)
                team.reset_password_code = reset_password_code
                team.reset_expires = reset_expires
                team.save()
                def mail_thread():
                    try:
                        subject = u"成都信息工程学院%s在线答题平台重置密码邮件"%settings.PLATFORM_MODE
                        body = u"你好，%s团队：\n\n这是成都信息工程学院%s在线答题平台重置登录密码的邮件，如非本人操作，无需做任何处理，如果多次受到该邮件的骚扰请联系管理员 ashin.myclover@gmail.com \n请务必在24小时内点击 http://%s/accounts/reset-password/%s/ 重置您的团队登录密码。\n\nby Syclover-阿小信"%(user.username, settings.PLATFORM_MODE, settings.PLATFORM_HOST, team.reset_password_code)
                        send_mail(subject, body, settings.EMAIL_HOST_USER, [user.email])
                    except Exception, e:
                        log.debug(u'找回密码邮件发送失败，%s'%str(e))

                threading.Thread(target=mail_thread, args=()).start()
                messages.add_message(request, messages.INFO, u'请查看你的注册邮箱,点击重置密码链接即可重置您的登录密码！')
            else:
                messages.add_message(request, messages.INFO, u'团队名称无法正确匹配团队邮箱，请检查您的输入信息是否正确！')
            
    return render_to_response('forget-password.html', {'form':form, }, context_instance=RequestContext(request))

def reset_password(request, reset_password_code=''):
    '''
        用户重置密码
    '''
    team = get_object_or_404(Team, reset_password_code=reset_password_code)
    if team.reset_expires < datetime.datetime.today():
        messages.add_message(request, messages.INFO, u'重置密码有效期限已过！')
        return HttpResponseRedirect(reverse('geek.geekchallenge.views.team_login', args=()))

    form = ResetPasswordForm()
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = team.user
            user.set_password(cd['password1'])
            user.save()
            messages.add_message(request, messages.INFO, u'密码重置成功，请重新登录！')
            return HttpResponseRedirect(reverse('geek.geekchallenge.views.team_login', args=()))

    return render_to_response('reset-password.html', {'form':form, }, context_instance=RequestContext(request))


@login_required
def change_password(request):
    '''
        修改密码视图
    '''
    form = ChangePasswordForm()
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.get(username=request.user.username)
            if not user.check_password(cd['old_password']): #验证旧密码
                messages.add_message(request, messages.INFO, u'当前密码错误！')
            else:
                user.set_password(cd['password1']) #设置新密码
                user.save()
                messages.add_message(request, messages.INFO, u'密码修改成功，请重新登录！')
                logout(request)
                return HttpResponseRedirect(reverse('geek.geekchallenge.views.team_login', args=()))
    return render_to_response('change-password.html', {'form':form, }, context_instance=RequestContext(request))

@login_required
def team_info(request):
    '''
        团队信息视图
    '''
    user = User.objects.get(username = request.user.username)
    #工作人员帐号跳转到后台，因为没有团队信息，查看会导致500
    if user.is_staff:
        return HttpResponseRedirect('/4dm!n')
    #参赛人员正常查看团队信息
    team = Team.objects.get(user=user)
    if request.method == 'POST':
        form = TeamInfoForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            team.leader_name = cd['leader_name']
            team.leader_number = cd['leader_number']
            team.institute = cd['institute']
            team.team_member = cd['team_member']
            team.motto = cd['motto']
            team.save() #保存user扩展字段
            messages.add_message(request, messages.INFO, u'修改成功！')
        else:
            messages.add_message(request, messages.INFO, u'请填写正确的字段！')
    return render_to_response('team-info.html', {'team':user, 'profile':team}, context_instance=RequestContext(request))

def rules(request):
    '''
        参赛规则视图
    '''
    geek_rules = Rules.objects.all()
    return render_to_response('rules.html', {'rules':geek_rules}, context_instance=RequestContext(request))

def check_answer(request):
    '''
        检查答案，并做出相应处理
    '''
    #answer = hash_answer(request.POST['answer'])
    answer = request.POST['answer']
    item_id = request.POST['item_id']
    user = request.user
    item = Item.objects.get(id=item_id)
    team = user.team_set.all()[0]
    #检验是否已答过此题
    answered = team in item.answered_by_team.all()
    if answered:
        messages.add_message(request, messages.INFO, u'对不起，该题您的团队已经完成此题，请勿重复提交')
    else:
        #没有答过该题，检验答案是否正确
        if answer == item.answer:
            #练习模式不加分
            if not item.is_practice:
                team.team_score += item.score
                team.answered_count += 1
                team.last_submit_time = datetime.datetime.now()
                team.save()
                item.answered_by_team.add(team)
            messages.add_message(request, messages.INFO, u'恭喜，答案正确，继续哟～')
        else:
            messages.add_message(request, messages.INFO, u'噢哦，答案错误，加油哟～')



@login_required
def challenge(request, type_id=None):
    '''
        比赛答题视图
    '''
    user = User.objects.get(username = request.user.username)
    #工作人员帐号跳转到后台，因为没有团队信息，查看会导致500
    if user.is_staff:
        return HttpResponseRedirect('/4dm!n')
    items = Item.objects.all()
    item_types = ItemType.objects.all()
    team = request.user.team_set.all()[0]
    
    if request.method == 'POST':
        check_answer(request)
    
    if type_id:
        typed_items = Item.objects.filter(item_type=type_id, is_released=True)
        return render_to_response('detail.html', {'typed_items':typed_items, 'team': team, 'item_types':item_types, 'type_id':int(type_id)}, context_instance=RequestContext(request))
    return render_to_response('challenge.html', {'items':items, 'item_types':item_types}, context_instance=RequestContext(request))

@login_required
def rank(request):
    '''
        得分排行视图
    '''
    teams = Team.objects.all()
    
    #排名
    rank_teams = []
    for rank,team in enumerate(teams):
        rank_teams.append((rank+1, team))
    #分页
    team_paginator = Paginator(rank_teams, 10)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        page_teams = team_paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_teams = team_paginator.page(team_paginator.num_pages)
    return render_to_response('rank.html', {'teams':rank_teams, 'page_teams':page_teams, 'team_paginator':team_paginator}, context_instance=RequestContext(request))


def show_notices(request):
    '''公告'''
    notices = Notices.objects.all()
    notices_paginator = Paginator(notices, 10)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        page_notices = notices_paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_notices = notices_paginator.page(notices_paginator.num_pages)
    return render_to_response('notices.html', {'notices':notices, 'page_notices':page_notices, 'notices_paginator':notices_paginator}, context_instance=RequestContext(request))

@staff_member_required
def admin_team_info(request):
    '''每支队伍答题情况'''
    teams = Team.objects.all()
    types = ItemType.objects.all()
    answered_items_by_teams = []
    for team in teams:
        answered_items = team.item_set.all()
        if answered_items:
            answered_items_by_teams.append((team, answered_items))

    return render_to_response('admin-team-info.html', {'answered_items_by_teams':answered_items_by_teams, 'teams':teams, 'types':types}, context_instance=RequestContext(request))
    
@staff_member_required
def admin_item_info(request):
    '''每题被答情况'''
    items = Item.objects.all()
    types = ItemType.objects.all()
    answered_items_and_count = []
    for item in items:
        answered_items_and_count.append((item, item.answered_by_team.count()))

    return render_to_response('admin-item-info.html', {'answered_items_and_count':answered_items_and_count, 'items':items}, context_instance=RequestContext(request))
