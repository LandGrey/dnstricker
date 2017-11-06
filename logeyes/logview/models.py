from django.db import models
from django.contrib import admin


class User(models.Model):
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    udomain = models.CharField(max_length=128)

    def __unicode__(self):
        return self.username


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'udomain')

admin.site.register(User, UserAdmin)


class WebLog(models.Model):
    user = models.ForeignKey(User)
    host = models.TextField('host', default='default')
    path = models.TextField('path', default='default')
    method = models.TextField('method', default='default')
    remote_addr = models.GenericIPAddressField('remote_addr', default='default')
    http_user_agent = models.TextField('user_agent', default='default')
    http_referer = models.TextField('referer', default='default')
    http_cookie = models.TextField('cookie', default='default')
    http_x_forwarded_for = models.TextField('x_forwarded_for', default='default')
    log_time = models.DateTimeField('time loged', auto_now_add=True)

    def __unicode__(self):
        return self.remote_addr

    class Meta:
        ordering = ['log_time']


class WebLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'host', 'path', 'method', 'remote_addr', 'http_user_agent', 'http_referer',
                    'http_cookie', 'log_time')

admin.site.register(WebLog, WebLogAdmin)


class DNSLog(models.Model):
    user = models.ForeignKey(User)
    client_ip = models.TextField('client_ip', default='default')
    client_port = models.TextField('client_port', default='default')
    query_host = models.TextField('query_host', default='default')
    record_type = models.TextField('record_type', default='default')
    log_time = models.DateTimeField('time loged', auto_now_add=True)

    def __unicode__(self):
        return self.host

    class Meta:
        ordering = ['log_time']


class DNSLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'client_ip', 'client_port', 'query_host', 'record_type', 'log_time')

admin.site.register(DNSLog, DNSLogAdmin)
