from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from drf_yasg import openapi


class User(AbstractUser):
    objects = UserManager()

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватарка')
    description = models.TextField(default="", verbose_name='Описание профиля', blank=True)

    schema = openapi.Schema(
        title='Пользователь',
        type=openapi.TYPE_OBJECT,
        required=['id', 'username', 'firstName', 'lastName', 'description'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, title='ID', description='ID пользователя'),
            'username': openapi.Schema(type=openapi.TYPE_STRING, title='Логин'),
            'firstName': openapi.Schema(type=openapi.TYPE_STRING, title='Имя'),
            'lastName': openapi.Schema(type=openapi.TYPE_STRING, title='Фамилия'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, title='Описание профиля'),
            'avatar': openapi.Schema(type=openapi.TYPE_STRING, title='Аватар', description='Ссылка на изображение'),
        }
    )


    @property
    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'description': self.description,
            'avatar': self.avatar.url if self.avatar else None,
        }

    @property
    def friends(self):
        return UserFriend.get_friends(self)

    @property
    def friend_requests(self):
        return UserFriend.get_friend_requests(self)

    @property
    def friend_requests_send(self):
        return UserFriend.get_friend_requests_send(self)

    @staticmethod
    def friends_ids(friends_queryset):
        return {"users": [friend.id for friend in friends_queryset]}

    friends_ids_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title='Пользователи',
        properties={
            'users': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                title='id пользователей',
                items=openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    title='ID',
                )
            )
        }
    )

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return " ".join((self.first_name, self.last_name)).strip() or self.username


class UserFriend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_friends', verbose_name='Пользователь')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_friends', verbose_name='Друг')

    is_friend = models.BooleanField(default=False, verbose_name='Запрос принят')

    class Meta:
        db_table = 'user_friends'
        verbose_name = 'Друг'
        verbose_name_plural = 'Друзья'

        unique_together = [['user', 'friend']]


    @classmethod
    def get_friends(cls, user):
        return (cls.objects.filter(user=user) | cls.objects.filter(friend=user)).filter(is_friend=True)

    @classmethod
    def get_friend_requests(cls, user):
        return cls.objects.filter(friend=user, is_friend=False)

    @classmethod
    def get_friend_requests_send(cls, user):
        return cls.objects.filter(user=user, is_friend=False)


