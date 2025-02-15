from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.admin_forms import UserCreationForm, UserChangeForm
from users.models import User, UserFriend


class UserFriendshipInline(admin.TabularInline):
    model = UserFriend
    extra = 0
    fk_name = 'user'

class BackFriendshipInline(admin.TabularInline):
    model = UserFriend
    extra = 0
    fk_name = 'friend'

class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ("username", "first_name", "last_name", "is_staff",)
    list_filter = ("is_staff",)
    fieldsets = (
        (None, {"fields": ("username", "first_name", "last_name", "email", "avatar", "password", "description",)}),
        ("Разрешения", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "email", "password1", "password2", "is_staff"
            )}
         ),
    )

    inlines = [UserFriendshipInline, BackFriendshipInline]

    search_fields = ("email", "username", "email", "first_name", "last_name")
    ordering = ("id",)


admin.site.register(User, CustomUserAdmin)
