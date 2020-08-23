from ..imdb_controller import Imdb
from ..models import Movie, Episode, Cast, Genre
from django.db import IntegrityError
import logging


def save_movie(imdbid):
    searcher = Imdb()
    try:
        movie_detail = searcher.fetch_movie_details(imdbid)
    except ValueError:
        return {'result': False, 'msg': 'Not found'}

    movie = Movie(imdbid=movie_detail['imdbid'], title=movie_detail['title'], cover_url=movie_detail['img'],
                  year=movie_detail['year'], plot=movie_detail['plot'],
                  rating=movie_detail['rating'])
    try:
        movie.save()
    except IntegrityError:
        return {'result': False, 'msg': 'Already Exists'}

    for director_name in movie_detail['directors']:
        director, created = Cast.objects.get_or_create(name=director_name)
        movie.directors.add(director)
    for genre_name in movie_detail['genres']:
        genre, created = Genre.objects.get_or_create(title=genre_name)
        movie.genres.add(genre)

    if movie_detail['kind'] == 'tv series':
        movie.is_series = True
        episode_number = 1
        season_compare = 0
        for season, episodes in movie_detail['episodes'].items():
            episode_number = 1
            for episode in episodes:
                # if season_compare != season:
                #     episode_number = 1
                episode = Episode(season=season, episode_number=episode_number, imdbid=episode['imdbid'],
                                  title=episode['title'],
                                  year=episode.get('year', None), cover_url=episode['img'], plot=episode['plot'],
                                  rating=episode['rating'], release_date=episode.get('release_date', None))
                episode.movie = movie
                episode_number += 1
                episode.save()
    movie.save()
    return {'result': True, 'msg': 'Success', 'movie': movie}


def save_all_movies_from_imdb(start_index=1):
    # from app.controllers.movies_controller import *
    # python manage.py shell --settings=fepisode.settings.dev
    limit = 9999999
    # basicconfig kullanma ayrı ayrı tanımla
    formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
    logger = logging.getLogger(__name__)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    filehandler = logging.FileHandler("/home/ozkan/Desktop/fepisode_all_save.log", mode='w')
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)
    logger.setLevel(logging.INFO)
    logger.info('start')
    
    for i in range(start_index, limit):
        imdbid = '{0:0>7}'.format(i)
        try:
            result = save_movie(imdbid)
            if result['result'] == True:
                print('okkk')
                # print('{} ({}) Saved - Key:{}'.format(result['movie'].title, result['movie'].year, str(i)))
                logger.info('%s (%s) Saved - Key:%s', result['movie'].title, str(result['movie'].year), str(i))
        except Exception as e:
            logger.exception(e)
