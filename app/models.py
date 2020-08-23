from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.utils.text import slugify


# Create your models here.
class BaseMovie(models.Model):
    imdbid = models.CharField(max_length=8, unique=True)
    slug = models.SlugField(unique=True, null=True)
    title = models.CharField(max_length=250)
    plot = models.TextField()
    cover_url = models.TextField(blank=True, null=True)
    year = models.CharField(max_length=4, null=True)
    rating = models.DecimalField(decimal_places=2, max_digits=5, null=True)
    release_date = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True


class Cast(models.Model):
    name = models.CharField(max_length=100)
    poster = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Movie(BaseMovie):
    is_series = models.BooleanField(default=False)
    directors = models.ManyToManyField(Cast, related_name='directors', blank=True)
    genres = models.ManyToManyField(Genre, related_name='genres', blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # generate slug on save
        if not self.slug:
            slug_title = slugify(self.title)
            self.slug = "{}-{}".format(slug_title, self.imdbid)
        super().save(*args, **kwargs)


class Episode(BaseMovie):
    movie = models.ForeignKey(Movie,
                              related_name='episodes',
                              on_delete=models.CASCADE)
    season = models.PositiveSmallIntegerField(null=True)
    episode_number = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        return '{} S{}E{}'.format(self.title, self.season, self.episode_number)

    def save(self, *args, **kwargs):
        # movie_slug = args[0].get('movie_slug', None)
        movie_slug = self.movie.slug
        if movie_slug is None:
            raise ValueError
        if not self.slug:
            self.slug = "{}--S{}E{}-{}".format(movie_slug, self.season, self.episode_number, self.imdbid)
        super().save(*args, **kwargs)


class Users(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, null=True)
    following = models.ManyToManyField(Movie, related_name='followings', blank=True)
    watched_movie = models.ManyToManyField(Movie, related_name='watched_movies', blank=True)
    watched_episode = models.ManyToManyField(Episode, related_name='watched_episodes', blank=True)

    def __str__(self):
        return self.name
