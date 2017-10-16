from django.contrib import admin

from .models import Question, Query

admin.site.register(Question)
admin.site.register(Query)
