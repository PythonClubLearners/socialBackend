from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class User(AbstractUser):
    objects = UserManager()

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватарка')
    description = models.TextField(default="", verbose_name='Описание профиля', blank=True)

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class UserFriends(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_friends', verbose_name='Пользователь')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_friends', verbose_name='Друг')

    is_friend = models.BooleanField(default=False, verbose_name='Запрос принят')

    class Meta:
        db_table = 'user_friends'
        verbose_name = 'Друг'
        verbose_name_plural = 'Друзья'


    @classmethod
    def get_friends(cls, user):
        return cls.objects.filter(user=user, is_friend=True)+cls.objects.filter(friend=user, is_friend=True)

    @classmethod
    def get_friend_requests(cls, user):
        return cls.objects.filter(friend=user, is_friend=False)




