from django.contrib import admin

from api.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    model = Post