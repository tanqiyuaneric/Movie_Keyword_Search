from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('keyword', views.keyword_detail),
    path('movie', views.movie_detail),
    path('search', views.keyword_search)
]
