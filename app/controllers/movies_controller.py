from ..imdb_controller import Imdb
from ..models import Movie, Episode, Cast, Genre
from django.db import IntegrityError
import logging
import multiprocessing
from threading import Thread


def save_movie(imdbid):
    searcher = Imdb()
    try:
        movie_detail = searcher.fetch_movie_details(imdbid)
    except ValueError:
        return {'result': False, 'msg': 'Not found'}
    except KeyError as keyError:
        return {'result': False, 'msg': 'Key {} Not found'.format(keyError)}

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
                episode_obj = Episode(season=season, episode_number=episode_number, imdbid=episode['imdbid'],
                                      title=episode['title'], year=episode.get('year', None),
                                      cover_url=episode['img'], plot=episode['plot'],
                                      release_date=episode.get('release_date', None))
                if episode.get('rating', None) is not None:
                    episode_obj.rating = float('%.2f' % episode['rating'])
                episode_obj.movie = movie
                episode_number += 1
                episode_obj.save()
    movie.save()
    return {'result': True, 'msg': 'Success', 'movie': movie}


def save_movie_to_db(imdbid, logger=logging.getLogger()):
    try:
        # logger.info('try %s', imdbid)
        result = save_movie(imdbid)
        if result['result'] == True:
            # print('{} ({}) Saved - Key:{}'.format(result['movie'].title, result['movie'].year, str(i)))
            logger.info('%s (%s) Saved - Key:%s', result['movie'].title, str(result['movie'].year), imdbid)
        else:
            logger.error('%s %s', result['msg'], imdbid)
    except Exception as e:
        logger.exception('Hata: %s %s', imdbid, e)


def save_movie_in_range(start, end, logger):
    for i in range(start, end, 10):
        threads = []
        for j in range(10):
            imdbid = '{0:0>7}'.format(i + j)
            try:
                t = Thread(target=save_movie_to_db, args=(imdbid, logger))
                t.start()
                threads.append(t)
            except Exception as e:
                logger.exception('Hata: %s %s', imdbid, e)
        for th in threads:
            th.join()


def save_all_movies_from_imdb(start_index=1, limit=9999999):
    # from app.controllers.movies_controller import *
    # python manage.py shell --settings=fepisode.settings.dev
    # limit = 9999999
    # basicconfig kullanma ayrı ayrı tanımla
    formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    logger = logging.getLogger(__name__)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    filehandler = logging.FileHandler("/home/ozkan/Desktop/fepisode_all_save.log")
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)
    logger.setLevel(logging.INFO)
    logger.info('start {}-{}'.format(str(start_index), str(limit)))
    # for a in range(start_index, limit, 100):
    #     pass
    a = int((limit - start_index) / 3)
    p1 = multiprocessing.Process(target=save_movie_in_range, args=(start_index, start_index + a, logger))
    p2 = multiprocessing.Process(target=save_movie_in_range, args=(start_index+a, start_index+a*2, logger))
    p3 = multiprocessing.Process(target=save_movie_in_range, args=(start_index+a*2, start_index+limit, logger))
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()
