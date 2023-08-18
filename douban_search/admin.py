from .models import Movie, Keyword, Comment
from django.contrib import admin
from django.db import models

# Register your models here.
admin.site.register(Movie)
admin.site.register(Keyword)
admin.site.register(Comment)
