from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import *
# Register your models here.

User=get_user_model()

admin.site.register(User)
admin.site.register(Role)
admin.site.register(Condition)
admin.site.register(Attribute)
admin.site.register(Department)
admin.site.register(AttributeImage)
admin.site.register(ForumPost)
admin.site.register(Comment)
admin.site.register(Like)
@admin.register(Symptoms)
class SymptomsAdmin(admin.ModelAdmin):
    search_fields = ['name']