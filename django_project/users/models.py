from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator



# Create your models here.

class User(AbstractUser):
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
    )

    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True, verbose_name='头像',default='avatar/default_avatar.png')
    phone = models.CharField(
        max_length=11,
        verbose_name='手机号',
        validators=[
            RegexValidator(
                regex=r'^1[3-9]\d{9}$',
                message='请输入正确的11位手机号码',
                code='invalid_phone'
            )
        ],
        blank=False,
        null=False,
        help_text='请输入11位手机号'
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male', verbose_name='性别')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['create_time']

    def __str__(self):
        return self.username
    
class UserLoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    login_time = models.DateTimeField(auto_now_add=True, verbose_name='登录时间')
    ip = models.GenericIPAddressField(verbose_name='登录IP')
    browser = models.CharField(max_length=50, verbose_name='浏览器')
    os = models.CharField(max_length=50, verbose_name='操作系统')
    is_success = models.BooleanField(default=True, verbose_name='登录是否成功')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')

    class Meta:
        db_table = 'user_login_log'
        verbose_name = '用户登录日志'
        verbose_name_plural = '用户登录日志'
        ordering = ['login_time']

    def __str__(self):
        return f"{self.user.username} - {self.ip} - {self.browser} - {self.os}"

