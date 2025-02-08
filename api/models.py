from django.db import models
from drf_yasg import openapi

from users.models import User


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание', blank=True, default='')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    image = models.ImageField(verbose_name='Изображение', upload_to='post_images/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')

    schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title='Пост',
        required=['title', 'description', 'created_date', 'author'],
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING, title='Заголовок'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, title='Описание'),
            'created_date': openapi.Schema(type=openapi.TYPE_NUMBER, title='Дата создания', description='Количество секунд с начала эпохи UNIX'),
            'image': openapi.Schema(type=openapi.TYPE_STRING, title='Изображение', description='Ссылка на изображение'),
            'author': openapi.Schema(type=openapi.TYPE_INTEGER, title='ID автора')
        }
    )

    collection_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title='Посты',
        properties={
            'posts': openapi.Schema(type=openapi.TYPE_ARRAY, title='Коллекция постов', items=schema)
        }
    )

    @property
    def json(self):
        return {
            'title': self.title,
            'description': self.description,
            'created_date': self.created_date.timestamp(),
            'image': self.image.url if self.image else None,
            'author': self.author.id,
        }
    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
