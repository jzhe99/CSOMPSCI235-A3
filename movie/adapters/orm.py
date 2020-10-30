from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime,
    ForeignKey
)
from sqlalchemy.orm import mapper, relationship

from movie.domain import model

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False)
)

reviews = Table(
    'reviews', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('users.id')),
    Column('movie_rank', ForeignKey('movies.rank')),
    Column('review', String(1024), nullable=False),
    Column('timestamp', DateTime, nullable=False)
)

movies = Table(
    'movies', metadata,
    Column('rank', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('discription', String(1024), nullable=False),
    Column('year', Integer, nullable=False),
    Column('runtime', Integer, nullable=False),
    Column('rating', String(255), nullable=False),
    Column('votes', Integer, nullable=False),
    Column('revenue', String(255), nullable=False),
    Column('metascore', Integer, nullable=False),
)

genres = Table(
    'genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(64), nullable=False)
)

movie_genres = Table(
    'movie_genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie_rank', ForeignKey('movies.rank')),
    Column('genre_id', ForeignKey('genres.id'))
)


def map_model_to_tables():
    mapper(model.User, users, properties={
        '_username': users.c.username,
        '_password': users.c.password,
        '_reviews': relationship(model.Review, backref='_user')
    })
    mapper(model.Review, reviews, properties={
        '_review': reviews.c.review,
        '_timestamp': reviews.c.timestamp
    })
    movies_mapper = mapper(model.Movie, movies, properties={
        '_rank': movies.c.rank,
        '_year': movies.c.year,
        '_title': movies.c.title,
        '_reviews': relationship(model.Review, backref='_movie')
    })
    mapper(model.Genre, genres, properties={
        '_genre_name': genres.c.name,
        '_genred_movie': relationship(
            movies_mapper,
            secondary=movie_genres,
            backref="_genres"
        )
    })
