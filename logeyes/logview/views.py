# coding=utf-8

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import (
    Paginator, InvalidPage, EmptyPage, PageNotAnInteger)
from django import forms
from models import *
from dnslog import settings
from django.contrib.auth import logout


def index(request):
    http_host = request.get_host()
    none_value = '<None>'
    if ":" in http_host:
        http_host = http_host.split(':')[0]
    request_method = request.META.get('REQUEST_METHOD', none_value)
    http_user_agent = request.META.get('HTTP_USER_AGENT', none_value)
    http_referer = request.META.get('HTTP_REFERER', none_value)
    http_cookie = request.META.get('HTTP_COOKIE', none_value)
    http_x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', none_value)
    try:
        remote_addr = request.META.get('HTTP_X_REAL_IP')
    except:
        remote_addr = request.META.get('REMOTE_ADDR')
    path = request.get_full_path()
    if http_host == settings.ADMIN_DOMAIN:
        return login(request)
    elif http_host.endswith(settings.DNS_DOMAIN):
        # httplog 记录处理流程
        subdomain = http_host.replace(settings.DNS_DOMAIN, '')
        if subdomain:
            domains = subdomain.split('.')
            if len(domains) >= 2:
                udomain = domains[-2]
                user = User.objects.filter(udomain__exact=udomain)
                if user:
                    weblog = WebLog(user=user[0], host=http_host, path=path, method=request_method,
                                    remote_addr=remote_addr, http_user_agent=http_user_agent, http_referer=http_referer,
                                    http_cookie=http_cookie, http_x_forwarded_for=http_x_forwarded_for)
                    weblog.save()
                    return HttpResponse("ok")
        return HttpResponseRedirect('http://192.168.1.1/')
    else:
        return HttpResponseRedirect('file:///')


class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=128)
    password = forms.CharField(label='密  码', widget=forms.PasswordInput())


def login(request):
    userid = request.session.get('userid', None)
    if userid:
        return logview(request, userid)
    if request.method == 'POST':
        uf = UserForm(request.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            user = User.objects.filter(username__exact=username, password__exact=password)
            if user:
                request.session['userid'] = user[0].id
                return logview(request, user[0].id)
            else:
                return render(request, 'login.html', {'uf': uf, 'error': u'用户名或密码错误'})
    else:
        uf = UserForm()
    return render(request, 'login.html', {'uf': uf})


def my_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def getpage(p):
    try:
        page = int(p)
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    return page


def logview(request, userid):
    user = User.objects.filter(id__exact=userid)[0]
    vardict = {}
    logtype = request.GET.get("logtype", 'dns')
    deltype = request.GET.get("del")
    if deltype == 'dns':
        DNSLog.objects.filter(user=user).delete()
        return HttpResponseRedirect('/?logtype=dns')
    if deltype == 'web':
        WebLog.objects.filter(user=user).delete()
        return HttpResponseRedirect('/?logtype=web')
    if logtype == 'dns':
        vardict['logtype'] = logtype
        dnspage = getpage(request.GET.get("dnspage", 1))
        paginator = Paginator(DNSLog.objects.filter(user=user), 10)
        try:
            dnslogs = paginator.page(dnspage)
        except(EmptyPage, InvalidPage, PageNotAnInteger):
            dnspage = paginator.num_pages
            dnslogs = paginator.page(paginator.num_pages)
        vardict['dnspage'] = dnspage
        vardict['pagerange'] = paginator.page_range
        vardict['dnslogs'] = dnslogs
        vardict['numpages'] = paginator.num_pages
    elif logtype == 'web':
        vardict['logtype'] = logtype
        webpage = getpage(request.GET.get("webpage", 1))
        paginator = Paginator(WebLog.objects.filter(user=user), 10)
        try:
            weblogs = paginator.page(webpage)
        except(EmptyPage, InvalidPage, PageNotAnInteger):
            webpage = paginator.num_pages
            weblogs = paginator.page(paginator.num_pages)
        vardict['webpage'] = webpage
        vardict['pagerange'] = paginator.page_range
        vardict['weblogs'] = weblogs
        vardict['numpages'] = paginator.num_pages
    else:
        return HttpResponseRedirect('/')
    vardict['userdomain'] = user.udomain + '.' + settings.DNS_DOMAIN
    vardict['udomain'] = str(user.udomain)
    vardict['admindomain'] = str(settings.ADMIN_DOMAIN)
    return render_to_response('views.html', vardict)


def api(request, logtype, udomain, hashstr):
    apistatus = False
    host = "%s.%s" % (hashstr, udomain)
    if logtype == 'dns':
        res = DNSLog.objects.filter(host__contains=host)
        if len(res) > 0:
            apistatus = True
    elif logtype == 'web':
        res = WebLog.objects.filter(path__contains=host)
        if len(res) > 0:
            apistatus = True
    else:
        return HttpResponseRedirect('/')
    return render(request, 'api.html', {'apistatus': apistatus})
