import csv
import os
from datetime import date, datetime
from typing import List

from bisect import insort_left, bisect_left

from werkzeug.security import generate_password_hash

from movie.adapters.repository import AbstractRepository
from movie.domain.model import User, Movie, Actor, Genre, Review, Director, make_genre_association, make_actor_association, make_review, make_director_association


class MemoryRepository(AbstractRepository):
    # Articles ordered by date, not id. id is assumed unique.

    def __init__(self):
        self._movies = list()
        self._movies_index = dict()
        self._genres = list()
        self._actors = list()
        self._directors = list()
        self._users = list()
        self._reviews = list()

    def rr(self):
        return self._movies[0]

    def add_user(self, user: User):
        self._users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self._users if user.user_name == username), None)

    def add_movie(self, movie: Movie):
        insort_left(self._movies, movie)
        self._movies_index[movie.rank] = movie

    def get_movie(self, rank: int) -> Movie:
        movie = None

        try:
            movie = self._movies_index[rank]
        except KeyError:
            pass  # Ignore exception and return None.

        return movie

    def get_movies_by_year(self, y) -> List[Movie]:
        target_movie = Movie(
            name=None,
            year1=y,
            rank=None,
        )
        matching_movie = list()

        try:
            for movie in self._movies:
                if movie.year == y:
                    matching_movie.append(movie)
        except ValueError:
            # No articles for specified date. Simply return an empty list.
            pass

        return matching_movie

    def get_number_of_movies(self):
        return len(self._movies)

    def get_first_movie(self):
        movie = None

        if len(self._movies) > 0:
            movie = self._movies[0]
        return movie

    def get_last_movie(self):
        movie = None

        if len(self._movies) > 0:
            movie = self._movies[-1]
        return movie

    def get_movies_by_rank(self, rank_list):
        # Strip out any ids in id_list that don't represent Article ids in the repository.
        existing_ranks = [rank for rank in rank_list if rank in self._movies_index]

        # Fetch the Articles.
        movie = [self._movies_index[rank] for rank in existing_ranks]
        return movie

    def add_genre(self, genre: Genre):
        self._genres.append(genre)

    def get_genre(self) -> List[Genre]:
        return self._genres

    def get_movie_ranks_for_genre(self, genre_name: str):
        # Linear search, to find the first occurrence of a Tag with the name tag_name.
        genre = next((genre for genre in self._genres if genre.genre_name == genre_name), None)

        # Retrieve the ids of articles associated with the Tag.
        if genre is not None:
            movie_ranks = [movie.rank for movie in genre.genre_movie]
        else:
            # No Tag with name tag_name, so return an empty list.
            movie_ranks = list()

        return movie_ranks

    def add_actor(self, actor:Actor):
        self._actors.append(actor)

    def get_actor(self) -> List[Actor]:
        return self._actors

    def get_movie_ranks_for_actor(self, actor_name: str):
        # Linear search, to find the first occurrence of a Tag with the name tag_name.
        actor = next((actor for actor in self._actors if actor.actor_full_name == actor_name), None)

        # Retrieve the ids of articles associated with the Tag.
        if actor is not None:
            movie_ranks = [movie.rank for movie in actor.actor_movie]
        else:
            # No Tag with name tag_name, so return an empty list.
            movie_ranks = list()

        return movie_ranks

    def add_director(self, director: Director):
        self._directors.append(director)

    def get_director(self) -> List[Director]:
        return self._directors

    def get_movie_ranks_for_director(self, director_name: str):
        # Linear search, to find the first occurrence of a Tag with the name tag_name.
        director = next((director for director in self._directors if director.director_full_name == director_name),
                        None)

        # Retrieve the ids of articles associated with the Tag.
        if director is not None:
            movie_ranks = [movie.rank for movie in director.directed_movie]
        else:
            # No Tag with name tag_name, so return an empty list.
            movie_ranks = list()

        return movie_ranks

    def get_year_of_previous_movie(self, movie: Movie):
        max_year = None
        prev_year_list = []
        try:
            for stored_movie in self._movies:
                if stored_movie.year < movie.year:
                    prev_year_list.append(stored_movie.year)
                    # break
            if len(prev_year_list) > 0:
                max_year = max(prev_year_list)
        except ValueError:
            # No earlier articles, so return None.
            pass
        return max_year

    def get_year_of_next_movie(self, movie: Movie):
        min_year = None
        next_year_list = []
        try:
            for stored_movie in self._movies:
                if stored_movie.year > movie.year:
                    next_year_list.append(stored_movie.year)
                    #break
            if len(next_year_list)>0:
                min_year = min(next_year_list)
        except ValueError:
            # No earlier articles, so return None.
            pass
        return min_year

    def movie_index(self, movie: Movie):
        index = bisect_left(self._movies, movie)
        if index != len(self._movies) and self._movies[index].year == movie.year:
            return index
        raise ValueError

    def get_movies_by_director(self, d) -> List[Director]:
        matching_movie = list()
        try:
            for director in self._directors:
                if director.director_full_name == d:
                    for movie in director.directed_movie:
                        matching_movie.append(movie)
        except ValueError:
            # No articles for specified date. Simply return an empty list.
            pass

        return matching_movie

    def add_review(self, review: Review):
        super().add_review(review)
        self._reviews.append(review)

    def get_reviews(self):
        return self._reviews


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def load_movies_and_genres_and_actors_and_directors(data_path: str, repo: MemoryRepository):
    genres = dict()
    actors = dict()
    directors = dict()
    for data_row in read_csv_file(os.path.join(data_path, 'Data1000Movies.csv')):

        movie_key = int(data_row[0])
        number_of_genres = 2
        movie_genres = sorted(data_row[number_of_genres].strip().split(','))
        number_of_actors = 5
        movie_actors = sorted(data_row[number_of_actors].strip().split(','))
        number_of_directors = 4
        movie_directors = sorted(data_row[number_of_directors].strip().split(','))

        # Add any new tags; associate the current article with tags.
        for genre in movie_genres:
            if genre not in genres.keys():
                genres[genre] = list()
            genres[genre].append(movie_key)
        #del data_row[-number_of_genres:]
        for actor in movie_actors:
            if actor not in actors.keys():
                actors[actor] = list()
            actors[actor].append(movie_key)

        for director in movie_directors:
            if director not in directors.keys():
                directors[director] = list()
            directors[director].append(movie_key)
        # Create Article object.

        movie = Movie(name=data_row[1], year1=int(data_row[6]), rank=int(data_row[0]))

        # Add the Article to the repository.
        repo.add_movie(movie)

    # Create Tag objects, associate them with Articles and add them to the repository.
    for genre_name in genres.keys():
        genre = Genre(genre_name)
        for movie_rank in genres[genre_name]:
            movie = repo.get_movie(movie_rank)
            make_genre_association(movie, genre)
        repo.add_genre(genre)

    for actor_name in actors.keys():
        actor = Actor(actor_name)
        for movie_rank in actors[actor_name]:
            movie = repo.get_movie(movie_rank)
            make_actor_association(movie, actor)
        repo.add_actor(actor)

    for director_name in directors.keys():
        director = Director(director_name)
        for movie_rank in directors[director_name]:
            movie = repo.get_movie(movie_rank)
            make_director_association(movie, director)
        repo.add_director(director)


def load_users(data_path: str, repo: MemoryRepository):
    users = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'users.csv')):
        user = User(name=data_row[1], password=generate_password_hash(data_row[2]))
        repo.add_user(user)
        users[data_row[0]] = user
    return users


def load_reviews(data_path: str, repo: MemoryRepository, users):
    for data_row in read_csv_file(os.path.join(data_path, 'reviews.csv')):
        review = make_review(
            review_text=data_row[3],
            user=users[data_row[1]],
            movie=repo.get_movie(int(data_row[2])),
            review_num=int(data_row[-1])
        )
        repo.add_review(review)


def populate(data_path: str, repo: MemoryRepository):
    # Load articles and tags into the repository.
    load_movies_and_genres_and_actors_and_directors(data_path, repo)

    # Load users into the repository.
    users = load_users(data_path, repo)

    # Load comments into the repository.
    load_reviews(data_path, repo, users)
