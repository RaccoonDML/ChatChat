from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name=u'用户', on_delete=True)
    name = models.CharField(max_length=32, verbose_name=u'昵称')
    signature = models.CharField(max_length=256, blank=True, null=True, verbose_name=u'签名')
    avator = models.ImageField(blank=True, null=True, verbose_name=u'头像', upload_to='uploads')
    friends = models.ManyToManyField('self', related_name='my_frients', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u'用户表'
        verbose_name_plural = u'用户表'


class Group(models.Model):
    name = models.CharField(max_length=64)
    brief = models.CharField(max_length=256, blank=True, null = True)
    owner = models.ForeignKey(UserProfile, on_delete=True)
    admins = models.ManyToManyField(UserProfile, blank=True, related_name='group_admins')
    menbers = models.ManyToManyField(UserProfile, blank=True, related_name='group_members')
    max_menbers = models.IntegerField(default=200)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = u'聊天组'
        verbose_name = u'聊天组'