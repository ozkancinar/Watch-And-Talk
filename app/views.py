from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from .imdb_controller import Imdb
from django.http import JsonResponse, Http404, HttpResponseRedirect, HttpResponseBadRequest
from .models import Movie, Episode, Cast, Genre
from .controllers.movies_controller import *
from django.urls import reverse
import json
from operator import itemgetter

# Create your views here.
def index(request):
    context = {}
    if request.method == 'POST':
        search_word = request.POST.get('movie_name')
        searcher = Imdb()
        search_result = searcher.search_movie(search_word)
        context = {
            'movies': search_result
        }

    return render(request, 'app/index.html', context)


def search_movie(request):
    # dbye bak en yüksek puanlı 3 kayıt
    search_string = request.GET.get('search_string')
    movies = Movie.objects.filter(title__icontains=search_string)[:5]
    data = []
    for movie in movies:
        data.append({
            'imdbid': movie.imdbid,
            'label': movie.title,
            'img': movie.cover_url,
            'year': movie.year,
            'slug': None
        })
    if len(data) < 5:
        searcher = Imdb()
        search_result = searcher.search_movie(search_string)
        for fetched_movie in search_result:
            if len(data) >= 5:
                continue
            data.append({
                'imdbid': fetched_movie['imdbid'],
                'label': fetched_movie['title'],
                'img': fetched_movie['img'],
                'year': fetched_movie['year'],
                'slug': None
            })
    json_response = json.dumps(data)
    return JsonResponse(data, safe=False)


def movie_detail_by_slug(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    context = {
        'movie': movie
    }
    return render(request, 'app/movie_detail.html', context)


def movie_save(request):
    if request.method != 'POST':
        raise HttpResponseBadRequest
    data = json.loads(request.body)
    imdbid = data.get('imdbid', None)
    if imdbid is None:
        raise ValueError

    save_result = save_movie(imdbid)
    if save_result['result'] == False:
        return JsonResponse({'error': save_result['msg']}, status=404)
    else:
        return JsonResponse(json.dumps({'slug': save_result['movie'].slug}), status=200, safe=False)


def display_search_results(request):
    search_string = request.GET.get('movie_name')
    movies = Movie.objects.filter(title__icontains=search_string).order_by('-rating')[:10]
    searcher = Imdb()
    search_result = searcher.search_movie(search_string)
    result = []
    for movie in movies:
        result.append({
            'imdbid': movie.imdbid,
            'title': movie.title,
            'img': movie.cover_url,
            'year': movie.year,
            'kind': '',
        })
        if movie.is_series:
            result[-1]['kind'] = 'tv_series'
        else:
            result[-1]['kind'] = 'movies'
    found = False
    for url_movie in search_result:
        for movie in movies:
            if movie.imdbid == url_movie['imdbid']:
                found = True
        if not found:
            result.append({
                'imdbid': url_movie['imdbid'],
                'title': url_movie['title'],
                'img': url_movie['img'],
                'year': str(url_movie['year']),
                'kind': url_movie['kind'],
            })
        found = False

    #TODO: sort by relevance 
    by_year = itemgetter('year')
    result.sort(key=by_year, reverse=True)
    context = {
        'movies': result
    }
    return render(request, 'app/movie_list.html', context)
