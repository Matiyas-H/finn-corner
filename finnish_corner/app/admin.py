from django.contrib import admin
from .models import Chat,Audio,Scenario
# Register your models here.



admin.site.register([Scenario, Chat, Audio])