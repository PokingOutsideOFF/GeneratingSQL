from django.contrib import admin
from .models import User, Profile, Chat_History

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Chat_History)
