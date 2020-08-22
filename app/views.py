from django.shortcuts import render, get_object_or_404, redirect
from .imdb_controller import Imdb
from django.http import JsonResponse, Http404, HttpResponseRedirect
from .models import Movie, Episode, Cast, Genre
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
            'year': movie.year
        })
    for fetched_movie in search_result:
        if len(data) >= 5:
            continue
        data.append({
            'imdbid': fetched_movie['imdbid'],
            'label': fetched_movie['title'],
            'img': fetched_movie['img'],
            'year': fetched_movie['year']
        })
    json_response = json.dumps(data)
    return JsonResponse(data, safe=False)


def movie_detail_by_slug(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    context = {
        'movie': movie
    }
    return render(request, 'app/movie_detail.html', context)


def movie_save(request, imdbid):
    searcher = Imdb()
    try:
        movie_detail = searcher.fetch_movie_details(imdbid)
    except ValueError:
        raise Http404
    movie = Movie(imdbid=movie_detail['imdbid'], title=movie_detail['title'], cover_url=movie_detail['img'],
                  year=movie_detail['year'], plot=movie_detail['plot'],
                  rating=movie_detail['rating'])
    for director_name in movie_detail['directors']:
        director = Cast.objects.get_or_create(name=director_name)
        movie.directors.add(director)
    for genre_name in movie_detail['genres']:
        genre = Genre.objects.get_or_create(title=genre_name)
        movie.genres.add(genre)

    if movie_detail['kind'] == 'tv series':
        movie.is_series = True
        episode_number = 1
        season_compare = 0
        for season, episode in movie_detail['episodes'].items():
            if season_compare != season:
                episode_number = 1
            episode = Episode(season=season, episode=episode_number, imdbid=episode['imdbid'], title=episode['title'],
                              year=episode['year'], img=episode['img'], plot=episode['plot'],
                              rating=episode['rating'], release_date=episode['release_date'])
            episode.movie = movie
            episode_number += 1
            episode.save()
    movie.save()
    slug = movie.slug

    url = reverse('movie_detail', kwargs={'slug': slug})
    return HttpResponseRedirect(url)
