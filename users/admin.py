from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.admin_forms import UserCreationForm, UserChangeForm
from users.models import User


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ("username", "is_staff",)
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

    search_fields = ("email", "username", "email")
    ordering = ("id",)


admin.site.register(User, CustomUserAdmin)
