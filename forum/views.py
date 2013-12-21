#-*- coding:utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import *
from geek.forum.models import *
from geek.forum.forms import *
import datetime
from django.utils import simplejson
from django.db.models import Q 
from itertools import chain

def replace_sensitive_words(content, replace_word="*"):
    sensitive_words = SensitiveWords.objects.all()
    for word in sensitive_words:
        if word.words in content:
            content = content.replace(word.words, replace_word)
    return content

def home(request):
    '''
        论坛主页视图
    '''
    areas = Area.objects.all()

    return render_to_response('forum-home.html', {"areas":areas}, context_instance=RequestContext(request))

def forum(request, forum_id):
    '''
        版块视图
    '''
    forum = get_object_or_404(Forum, id=forum_id)
    form = NewThreadForm()

    #分页
    threads = forum.thread_set.exclude(is_toped=True)
    threads_paginator = Paginator(threads, 20)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        paged_threads = threads_paginator.page(page)
    except (EmptyPage, InvalidPage):
        paged_threads = threads_paginator.page(threads_paginator.num_pages)

    #用于导航定位链接
    parents = []
    parent = forum.parent
    while parent:
        parents.append(parent)
        parent = parent.parent

    #热门主题
    def by_reply_count(i):
        return i.reply_count()
    hot_threads = list(threads.order_by("-clicked")[:5])#按点击量
    hot_threads.sort(key=by_reply_count, reverse=True) #按回复数

    toped_threads = Thread.objects.filter(is_toped=True)

    #最新帖子
    latest_threads = Thread.objects.all()[:5]

    return render_to_response('threads-list.html', {"forum":forum, 'parents':parents, "paged_threads":paged_threads, "threads_paginator":threads_paginator, "hot_threads":hot_threads, "latest_threads":latest_threads, 'form':form, 'toped_threads':toped_threads}, context_instance=RequestContext(request))

def thread(request, forum_id, thread_id):
    '''
        帖子视图
    '''
    forum = get_object_or_404(Forum, id=forum_id)
    thread = get_object_or_404(Thread, forum=forum, id=thread_id)
    thread.clicked += 1
    thread.save()

    form = NewThreadForm()
    reply_form = ReplyForm()
    edit_form = NewThreadForm(initial={'title':thread.title, 'content':thread.content})

    #用于导航定位链接
    parents = []
    parent = thread.forum.parent
    while parent:
        parents.append(parent)
        parent = parent.parent

    event_id = ""
    try:
        event_id = int(request.GET['reading'])
    except Exception, e:
        pass
        print e
    if event_id != "" and request.user.is_authenticated():
        event = get_object_or_404(Event, id = event_id, at_team = request.user)
        event.is_readed = True
        event.save()


    return render_to_response("thread.html", {"thread":thread, "parents":parents, "form":form, "edit_form":edit_form, "reply_form":reply_form}, context_instance=RequestContext(request))

@login_required
def new_thread(request, forum_id):
    '''
        创建新帖
    '''
    forum = get_object_or_404(Forum, id=forum_id)
    form = NewThreadForm()
    if request.method == 'POST':
        form = NewThreadForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            team = get_object_or_404(Team, user=request.user)
            new_thread = Thread(forum=forum, author=team, title=replace_sensitive_words(cd['title']), content=replace_sensitive_words(cd['content']))
            new_thread.save()
            messages.add_message(request, messages.INFO, u'帖子发表成功！')
            return HttpResponseRedirect("/forum/%s/%s/"%(forum.id, new_thread.id))
        else:
            messages.add_message(request, messages.INFO, u'发帖失败，请填写帖子标题和内容！')
    return HttpResponseRedirect("/forum/%s/"%forum.id)

@login_required
def edit_thread(request, forum_id, thread_id):
    '''
        编辑帖子
    '''
    forum = get_object_or_404(Forum, id=forum_id)
    team = get_object_or_404(Team, user=request.user)
    thread = get_object_or_404(Thread, id=thread_id, forum=forum, author=team)
    if request.method == 'POST':
        form = NewThreadForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            thread.title=replace_sensitive_words(cd['title'])
            thread.content=replace_sensitive_words(cd['content'])
            thread.update_time=datetime.datetime.now()
            thread.save()
            data = {'title':thread.title, 'content':thread.content, 'time':thread.update_time.strftime('%Y-%m-%d %H:%M:%S')}
            data = simplejson.dumps(data)
            return HttpResponse(data, mimetype="application/json")
    return HttpResponse("error")

@login_required
def reply(request, forum_id, thread_id):
    '''
        回复帖子
    '''
    forum = get_object_or_404(Forum, id=forum_id)
    thread = get_object_or_404(Thread, id=thread_id, forum=forum)
    team = get_object_or_404(Team, user=request.user)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            reply = Reply(thread=thread, author=team, content=replace_sensitive_words(cd['content']))
            reply.save()
            data = {'author':request.user.username, 'institute':team.institute, 'score':team.team_score, 'count':team.answered_count,\
                    'motto':team.motto, 'time':reply.submit_time.strftime('%Y-%m-%d %H:%M:%S'), 'content':reply.content, 'floor':Reply.objects.filter(thread=thread).count(), 'reply_id':reply.id}
            data = simplejson.dumps(data)
            return HttpResponse(data, mimetype="application/json")
    return HttpResponse("error")

@login_required
def edit_reply(request, reply_id):
    """修改回复"""
    team = get_object_or_404(Team, user=request.user)
    reply = get_object_or_404(Reply, id=reply_id, author=team)
    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            reply.content = replace_sensitive_words(cd['content'])
            reply.update_time = datetime.datetime.now()
            reply.save()
            data = {'new_content':reply.content}
            data = simplejson.dumps(data)
            return HttpResponse(data, mimetype="application/json")
    return HttpResponse("error")

def search_thread(request):
    keyword = request.REQUEST['keyword']
    results = Thread.objects.filter(Q(title__icontains=keyword)|Q(content__icontains=keyword))    
    #最新帖子
    latest_threads = Thread.objects.all()[:5]

    #分页
    threads_paginator = Paginator(results, 20)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        paged_threads = threads_paginator.page(page)
    except (EmptyPage, InvalidPage):
        paged_threads = threads_paginator.page(threads_paginator.num_pages)

    return render_to_response('search-result.html', {"results":results, "keyword":keyword, 'latest_threads':latest_threads, "paged_threads":paged_threads, "threads_paginator":threads_paginator}, context_instance=RequestContext(request))
    
def elited_thread(request):
    
    #最新帖子
    latest_threads = Thread.objects.all()[:5]

    results = Thread.objects.filter(is_elite=True)
    
    #分页
    threads_paginator = Paginator(results, 20)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        paged_threads = threads_paginator.page(page)
    except (EmptyPage, InvalidPage):
        paged_threads = threads_paginator.page(threads_paginator.num_pages)

    return render_to_response('elited-thread.html', {"results":results, 'latest_threads':latest_threads, "paged_threads":paged_threads, "threads_paginator":threads_paginator}, context_instance=RequestContext(request))

@login_required
def my_threads(request):
    
    #最新帖子
    latest_threads = Thread.objects.all()[:5]
    team = get_object_or_404(Team, user=request.user)
    replies = Reply.objects.filter(author=team)
    re_threads = [reply.thread for reply in replies]
    results = list(set(chain(Thread.objects.filter(author=team),re_threads)))
    results.reverse()

    
    #分页
    threads_paginator = Paginator(results, 20)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        paged_threads = threads_paginator.page(page)
    except (EmptyPage, InvalidPage):
        paged_threads = threads_paginator.page(threads_paginator.num_pages)

    return render_to_response('my-threads.html', {"results":results, 'latest_threads':latest_threads, "paged_threads":paged_threads, "threads_paginator":threads_paginator}, context_instance=RequestContext(request))


@login_required
def at_me(request):
    
    #最新帖子
    latest_threads = Thread.objects.all()[:5]

    #回复事件
    results = Event.objects.filter(at_team = request.user, is_deleted=False)
    unread_count = Event.objects.filter(at_team = request.user, is_deleted=False, is_readed = False).count()
    
    #分页
    events_paginator = Paginator(results, 15)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        paged_events = events_paginator.page(page)
    except (EmptyPage, InvalidPage):
        paged_events = events_paginator.page(events_paginator.num_pages)

    return render_to_response('at-me.html', {"results":results,'unread_count':unread_count, 'latest_threads':latest_threads, "paged_events":paged_events, "events_paginator":events_paginator}, context_instance=RequestContext(request))


@login_required
def readed_news(request, news_id):
    news = get_object_or_404(Event, id=news_id, at_team=request.user)
    if request.method == 'POST':
        news.is_readed=True
        news.save()
        return HttpResponse("success")
    return HttpResponse("error")

@login_required
def delete_news(request, news_id):
    news = get_object_or_404(Event, id=news_id, at_team=request.user)
    if request.method == 'POST':
        news.is_deleted = True
        news.save()
        return HttpResponse("success")
    return HttpResponse("error")


@login_required
def new_at_num(request):
    unread_count = Event.objects.filter(at_team = request.user, is_deleted=False, is_readed = False).count()
    return HttpResponse(unread_count)

@login_required
def nearest_users(request):
    threads = Thread.objects.all()
    replies = Reply.objects.all()
    users = [thread.author.user.username for thread in threads]
    users.extend([reply.author.user.username for reply in replies])
    users = set(users)
    if request.user.username in users:
        users.remove(request.user.username)

    user_name_list = []
    for user in users:
        user_name_list.append({}.fromkeys(('user', 'name'), user))

    show_count = 15
    if len(user_name_list) > show_count:
        user_name_list = user_name_list[:show_count]
    data = simplejson.dumps(user_name_list)
    return HttpResponse(data, mimetype="application/json")
