from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from douban_search.models import Keyword, Movie, Keyword_Info


def index(request):
    keywords = Keyword.objects.all().order_by('-count')[:10]
    if not request.LANGUAGE_CODE == 'zh-hans':
        keywords = [Keyword_en(k) for k in keywords]
    return render(request, 'index.html', {'keywords': keywords})


def keyword_detail(request):
    try:
        keyword = Keyword.objects.get(keyword=request.GET.get('keyword', ''))
    except Keyword.DoesNotExist:
        return HttpResponse(_('not found'))

    movies = Movie.objects.filter(keywords__keyword__contains=keyword)
    if not request.LANGUAGE_CODE == 'zh-hans':
        keyword = Keyword_en(keyword)
        movies = [Movie_en(m) for m in movies]
    return render(request, 'keyword_detail.html', {'keyword': keyword, 'movies': movies})


def movie_detail(request):
    try:
        movie = Movie.objects.get(name1=request.GET.get('name', ''))
    except Keyword.DoesNotExist or Movie.DoesNotExist:
        return HttpResponse(_('not found'))

    keywords_infos = Keyword_Info.objects.filter(movie=movie).order_by('-count')[:20]
    if not request.LANGUAGE_CODE == 'zh-hans':
        keywords_infos = [Keyword_en(k) for k in keywords_infos]
        movie = Movie_en(movie)
    return render(request, 'movie_detail.html', {'movie': movie, 'keywords_infos': keywords_infos})


def keyword_search(request):
    pattern = {}
    name = request.GET.get('name', '')
    if name:
        if not request.LANGUAGE_CODE == 'zh-hans':
            pattern['keyword2__contains'] = name
        else:
            pattern['keyword__contains'] = name
    results = Keyword.objects.filter(**pattern)

    # This is NOOOOOOOOOOT an elegant implementation of translating the search results. However, this is the first
    # way I came up with under the limited time
    results = [TranslatedResult(r, request.LANGUAGE_CODE == 'zh-hans') for r in results]
    success = False if len(results) == 0 else True

    return render(request, 'search.html', {'result': results, 'success': success})


class TranslatedResult:
    def __init__(self, keyword, is_zh):
        self.keyword = keyword if is_zh else Keyword_en(keyword)
        self.movie = keyword.movie_set.all() if is_zh else [Movie_en(i) for i in keyword.movie_set.all()]

    def __str__(self):
        return f'TranslatedResult for {str(self.keyword)}'


class Movie_en:
    def __init__(self, movie: Movie):
        self.name1 = movie.name1
        if movie.name2:
            self.name2 = movie.name2
        else:
            self.name2 = movie.name1 + ' (not translated yet)'
        self.url = movie.url

    def __str__(self):
        return self.name2


class Keyword_en:
    def __init__(self, keyword):
        self.count = keyword.count
        if isinstance(keyword, Keyword):
            keyword = keyword
        else:
            keyword = keyword.keyword
        self.keyword = keyword.keyword
        if keyword.keyword2:
            self.keyword_en = keyword.keyword2[:-1]
        else:
            self.keyword_en = keyword.keyword + ' (not translated yet)'

    def __str__(self):
        return self.keyword_en
