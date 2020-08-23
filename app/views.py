from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from .imdb_controller import Imdb
from django.http import JsonResponse, Http404, HttpResponseRedirect, HttpResponseBadRequest
from .models import Movie, Episode, Cast, Genre
from .controllers.movies_controller import *
from django.urls import reverse
import json


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
    movies = Movie.objects.filter(title__icontains=search_string)[:3]
    searcher = Imdb()
    search_result = searcher.search_movie(search_string)
    data = []
    for movie in movies:
        data.append({
            'imdbid': movie.imdbid,
            'label': movie.title,
            'img': movie.cover_url,
            'year': movie.year,
            'slug': None
        })
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

    # searcher = Imdb()
    # try:
    #     movie_detail = searcher.fetch_movie_details(imdbid)
    # except ValueError:
    #     raise Http404
    # movie = Movie(imdbid=movie_detail['imdbid'], title=movie_detail['title'], cover_url=movie_detail['img'],
    #               year=movie_detail['year'], plot=movie_detail['plot'],
    #               rating=movie_detail['rating'])
    # try:
    #     movie.save()
    # except IntegrityError:
    #     return JsonResponse({'error': 'Already exists'}, status=400)
    # for director_name in movie_detail['directors']:
    #     director, created = Cast.objects.get_or_create(name=director_name)
    #     movie.directors.add(director)
    # for genre_name in movie_detail['genres']:
    #     genre, created = Genre.objects.get_or_create(title=genre_name)
    #     movie.genres.add(genre)
    #
    # if movie_detail['kind'] == 'tv series':
    #     movie.is_series = True
    #     episode_number = 1
    #     season_compare = 0
    #     for season, episodes in movie_detail['episodes'].items():
    #         episode_number = 1
    #         for episode in episodes:
    #             # if season_compare != season:
    #             #     episode_number = 1
    #             episode = Episode(season=season, episode_number=episode_number, imdbid=episode['imdbid'], title=episode['title'],
    #                               year=episode.get('year', None), cover_url=episode['img'], plot=episode['plot'],
    #                               rating=episode['rating'], release_date=episode.get('release_date', None))
    #             episode.movie = movie
    #             episode_number += 1
    #             episode.save()
    # slug = movie.slug
    #
    # return JsonResponse(json.dumps({'slug': slug}), status=200, safe=False)
