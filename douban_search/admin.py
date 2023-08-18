from .models import Movie, Keyword
from django.contrib import admin
from django.db import models

# Register your models here.
admin.site.register(Movie)
admin.site.register(Keyword)
