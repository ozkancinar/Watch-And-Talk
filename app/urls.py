from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search_movie', views.search_movie, name='search_movie'),
    path('movie_detail/<slug:slug>', views.movie_detail_by_slug, name='movie_detail'),
    path('movie_save/<str:imdbid>', views.movie_save, name='movie_save')
]
