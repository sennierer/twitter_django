from django.contrib import admin
from .models import Account, Message, Project

# Register your models here.
admin.site.register(Account)
admin.site.register(Message)
admin.site.register(Project)
