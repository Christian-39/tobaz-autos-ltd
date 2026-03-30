from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['profile_image', 'phone', 'address', 'city', 'country', 'user_type', 'bio']


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type']
    
    def get_user_type(self, obj):
        return obj.profile.user_type
    get_user_type.short_description = 'User Type'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'country', 'user_type', 'created_at']
    list_filter = ['user_type', 'country']
    search_fields = ['user__username', 'user__email', 'phone']
