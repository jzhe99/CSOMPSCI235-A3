import csv
import os

from datetime import date
from typing import List

from sqlalchemy import desc, asc
from sqlalchemy.engine import Engine
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from werkzeug.security import generate_password_hash

from sqlalchemy.orm import scoped_session
from flask import _app_ctx_stack

from movie.domain.model import User, Movie, Review, Genre, Actor, Director
from movie.adapters.repository import AbstractRepository

genres = None
directors = None
actors = None

class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.add(user)
            scm.commit()

    def get_user(self, username) -> User:
        user = None
        try:
            user = self._session_cm.session.query(User).filter_by(_username=username).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return user

    def add_movie(self, movie: Movie):
        with self._session_cm as scm:
            scm.session.add(movie)
            scm.commit()

    def get_movie(self, rank: int) -> Movie:
        movie = []
        try:
            movie = self._session_cm.session.query(Movie).filter(Movie.rank == rank).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return movie

    def get_movies_by_year(self, target_year: int) -> List[Movie]:
        if target_year is None:
            movies = self._session_cm.session.query(Movie).all()
            return movies
        else:
            # Return articles matching target_date; return an empty list if there are no matches.
            movies = self._session_cm.session.query(Movie).filter(Movie.year == target_year).all()
            return movies

    def get_number_of_articles(self):
        number_of_movies = self._session_cm.session.query(Movie).count()
        return number_of_movies

    def get_first_article(self):
        movie = self._session_cm.session.query(Movie).first()
        return movie

    def get_last_article(self):
        movie = self._session_cm.session.query(Movie).order_by(desc(Movie.rank)).first()
        return movie

    def get_movies_by_rank(self, rank_list):
        movies = self._session_cm.session.query(Movie).filter(Movie.rank.in_(rank_list)).all()
        return movies

    def get_movie_ranks_for_genre(self, genre_name: str):
        movie_ranks = []

        # Use native SQL to retrieve article ids, since there is no mapped class for the article_tags table.
        row = self._session_cm.session.execute('SELECT rank FROM genres WHERE name = :genre_name', {'genre_name': genre_name}).fetchone()

        if row is None:
            # No tag with the name tag_name - create an empty list.
            movie_ranks = list()
        else:
            genre_rank = row[0]

            # Retrieve article ids of articles associated with the tag.
            movie_ranks = self._session_cm.session.execute(
                    'SELECT movie_rank FROM movie_genres WHERE genre_rank = :genre_rank ORDER BY movie_rank ASC',
                    {'genre_rank': genre_rank}
            ).fetchall()
            movie_ranks = [rank[0] for rank in movie_ranks]

        return movie_ranks

    def get_year_of_previous_movie(self, movie: Movie):
        result = None
        prev = self._session_cm.session.query(Movie).filter(Movie.year < movie.year).order_by(desc(Movie.year)).first()

        if prev is not None:
            result = prev.year

        return result

    def get_year_of_next_movie(self, movie: Movie):
        result = None
        next = self._session_cm.session.query(Movie).filter(Movie.year > movie.year).order_by(asc(Movie.year)).first()

        if next is not None:
            result = next.year

        return result

    def get_genre(self) -> List[Genre]:
        genres = self._session_cm.session.query(Genre).all()
        return genres

    def add_genre(self, genre: Genre):
        with self._session_cm as scm:
            scm.session.add(genre)
            scm.commit()

    def get_actor(self) -> List[Actor]:
        actors = self._session_cm.session.query(Actor).all()
        return actors

    def add_actor(self, actor: Actor):
        with self._session_cm as scm:
            scm.session.add(actor)
            scm.commit()

    def get_director(self) -> List[Director]:
        directors = self._session_cm.session.query(Director).all()
        return directors

    def add_director(self, director: Director):
        with self._session_cm as scm:
            scm.session.add(director)
            scm.commit()


    def get_reviews(self) -> List[Review]:
        reviews = self._session_cm.session.query(Review).all()
        return reviews

    def add_review(self, review: Review):
        super().add_review(review)
        with self._session_cm as scm:
            scm.session.add(review)
            scm.commit()

def movie_record_generator(filename: str):
    with open(filename, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)
        # Read first line of the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            movie_data = row
            movie_key = movie_data[0]
            # Strip any leading/trailing white space from data read.
            movie_data = [item.strip() for item in movie_data]
            number_of_genres = len(movie_data)-2
            movie_genres = movie_data[-number_of_genres:-number_of_genres+1]
            # Add any new tags; associate the current article with tags.
            for genre in movie_genres:
                if genre not in genres.keys():
                    genres[genre] = list()
                genres[genre].append(movie_key)
            del movie_data[-number_of_genres:-number_of_genres+1]

            number_of_actors = len(movie_data) - 4
            movie_actors = movie_data[-number_of_actors:-number_of_actors+1]
            for actor in movie_actors:
                if actor not in actors.keys():
                    actors[actor] = list()
                actors[actor].append(movie_key)
            del movie_data[-number_of_actors:-number_of_actors+1]

            number_of_director = len(movie_data) - 3
            movie_director = movie_data[-number_of_director:-number_of_director + 1]
            for director in movie_director:
                if director not in directors.keys():
                    directors[director] = list()
                directors[director].append(movie_key)
            del movie_data[-number_of_director:-number_of_director + 1]

            yield movie_data


def get_genre_records():
    genre_records = list()
    genre_key = 0

    for genre in genres.keys():
        genre_key = genre_key + 1
        genre_records.append((genre_key, genre))
    return genre_records


def movie_genres_generator():
    movie_genres_key = 0
    genre_key = 0

    for genre in genres.keys():
        genre_key = genre_key + 1
        for movie_key in genres[genre]:
            movie_genres_key = movie_genres_key + 1
            yield movie_genres_key, movie_key, genre_key


def generic_generator(filename, post_process=None):
    with open(filename) as infile:
        reader = csv.reader(infile)

        # Read first line of the CSV file.
        next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]

            if post_process is not None:
                row = post_process(row)
            yield row


def process_user(user_row):
    user_row[2] = generate_password_hash(user_row[2])
    return user_row


def populate(engine: Engine, data_path: str):
    conn = engine.raw_connection()
    cursor = conn.cursor()

    global genres
    genres = dict()
    global actors
    actors = dict()
    global directors
    directors = dict()

    insert_movies = """
        INSERT INTO movies (
        rank, title, discription, year, runtime, rating, votes, revenue, metascore)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.executemany(insert_movies, movie_record_generator(os.path.join(data_path, 'Data1000Movies.csv')))

    insert_genres = """
        INSERT INTO genres (
        id, name)
        VALUES (?, ?)"""
    cursor.executemany(insert_genres, get_genre_records())

    insert_movie_genres = """
        INSERT INTO movie_genres (
        id, movie_rank, genre_id)
        VALUES (?, ?, ?)"""
    cursor.executemany(insert_movie_genres, movie_genres_generator())

    insert_users = """
        INSERT INTO users (
        id, username, password)
        VALUES (?, ?, ?)"""
    cursor.executemany(insert_users, generic_generator(os.path.join(data_path, 'users.csv'), process_user))

    insert_reviews = """
        INSERT INTO reviews (
        id, user_id, movie_rank, review, timestamp)
        VALUES (?, ?, ?, ?, ?)"""
    cursor.executemany(insert_reviews, generic_generator(os.path.join(data_path, 'reviews.csv')))

    conn.commit()
    conn.close()

'''
defpopulate(session_factory, data_path, data_filename):filename = os.path.join(data_path, data_filename)movie_file_reader= MovieFileReader(filename)movie_file_reader.read_csv_file()session = session_factory()# This takes all movies from the csv file (represented as domain model objects) and adds them to the # database. If the uniqueness of directors, actors, genres is correctly handled, and the relationships# are correctly set up in the ORM mapper, then all associations will be dealt with as well!formovie inmovie_file_reader.dataset_of_movies:session.add(movie)session.commit()
'''