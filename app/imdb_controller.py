from imdb import IMDb

class Imdb:

    def __init__(self):
        pass

    def search_movie(self, search_str):
        movie_finder = IMDb()
        movies = movie_finder.search_movie(title=search_str, results=5)
        result = []
        for movie in movies[:5]:
            if movie['kind'] != 'tv series' and movie['kind'] != 'movie':
                continue
            # movie_detail = movie_finder.get_movie(movie.movieID)
            result_obj = {
                'imdbid': movie.movieID,
                'title': movie['title'],
                'img': movie['full-size cover url'],
                'year': movie['year'],
                'kind': movie['kind']
                # 'plot': movie_detail['plot'],
                # 'rating': movie_detail['rating']
            }
            result.append(result_obj)
        return result

    def fetch_movie_details(self, movieID):
        season_episodes = {}
        episodes = {}
        movie_finder = IMDb()
        movie = movie_finder.get_movie(movieID)
        if movie is None:
            raise ValueError
        if movie['kind'] == 'tv series':
            movie_finder.update(movie, 'episodes')
            number_seasons = movie['number of seasons']
            for season_num in range(1, number_seasons + 1):
                season = movie['episodes'][season_num]
                episodes[season_num] = []
                for key, episode in season.items():
                    episodes[season_num].append({
                        'imdbid': episode.movieID,
                        'title': episode['title'],
                        'year': episode.get('year', None),
                        'img': episode.get('cover url', None),
                        'plot': episode['plot'],
                        'rating': episode.get('rating', None),
                        'release_date': None
                    })

        movie_detail = {
            'imdbid': movieID,
            'title': movie['title'],
            'img': movie['full-size cover url'],
            'year': movie.get('year', None),
            'kind': movie['kind'],
            'directors': [],
            'plot': movie['plot'],  # list
            'rating': movie['rating'],
            'genres': movie['genres'],
            'number of seasons': movie.get('number of seasons', None),
            'number of episodes': movie.get('number of episodes', None),
            'episodes': episodes,
            'series years': movie.get('series years', None)
        }
        if 'directors' in movie:
            movie_detail['directors'] = [director for director in movie['directors']]
        return movie_detail

    def save_movie_to_db(self):
        pass
