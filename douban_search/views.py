from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.utils.translation import gettext as _

from douban_search.models import Keyword, Movie


# Create your views here.
def index(request):
    return render(request, 'index.html')


def keyword_detail(request):
    try:
        keyword = Keyword.objects.get(keyword=request.GET.get('keyword', ''))
    except Keyword.DoesNotExist:
        return HttpResponse(_('not found'))
    movies = Movie.objects.filter(keywords__keyword__contains=keyword)
    return render(request, 'keyword_detial.html', {'keyword': keyword, 'movies': movies})


def movie_detail(request):
    try:
        movie = Movie.objects.get(name=request.GET.get('name', ''))
    except Keyword.DoesNotExist:
        return HttpResponse(_('无法找到'))
    keywords = Keyword.objects.get(keyword=movie.keywords)
    name = movie.name
    url = movie.url
    return render(request, 'movie_detial.html', {'keywords': keywords, 'name': name, 'url': url})


def keyword_search(request):
    pattern = {}
    name = request.GET.get('name', '')
    if name:
        pattern['keyword__contains'] = name
    result = Keyword.objects.filter(**pattern).order_by('-count')
    if len(result) == 0:
        success = False
    else:
        success = True
    return render(request, 'search.html', {'result': result,  'success': success})
