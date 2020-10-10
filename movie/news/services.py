from typing import List, Iterable

from movie.adapters.repository import AbstractRepository
from movie.domain.model import make_review, Movie, Review, Genre, Actor, Director


class NonExistentArticleException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_review(movie_rank: int, review_text: str, username: str, repo: AbstractRepository, review_int: int):
    # Check that the article exists.
    movie = repo.get_movie(movie_rank)
    if movie is None:
        raise NonExistentArticleException

    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException

    # Create comment.
    review = make_review(review_text, user, movie, review_int)

    # Update the repository.
    repo.add_review(review)


def get_movie(movie_rank: int, repo: AbstractRepository):
    movie = repo.get_movie(movie_rank)

    if movie is None:
        raise NonExistentArticleException

    return movie_to_dict(movie)


def get_first_movie(repo: AbstractRepository):

    movie = repo.get_first_movie()

    return movie_to_dict(movie)


def get_last_movie(repo: AbstractRepository):

    movie = repo.get_last_movie()
    return movie_to_dict(movie)


def get_movies_by_year(y, repo: AbstractRepository):
    # Returns articles for the target date (empty if no matches), the date of the previous article (might be null), the date of the next article (might be null)

    movie = repo.get_movies_by_year(y)

    movies_dto = list()
    prev_year = next_year = None

    if len(movie) > 0:
        prev_year = repo.get_year_of_previous_movie(movie[0])
        next_year = repo.get_year_of_next_movie(movie[0])

        # Convert Articles to dictionary form.
        movies_dto = movies_to_dict(movie)

    return movies_dto, prev_year, next_year


def get_movie_ranks_for_genre(genre_name, repo: AbstractRepository):
    movie_ranks = repo.get_movie_ranks_for_genre(genre_name)

    return movie_ranks

def get_movie_ranks_for_actor(actor_name, repo: AbstractRepository):
    movie_ranks = repo.get_movie_ranks_for_actor(actor_name)

    return movie_ranks


def get_movie_ranks_for_director(director_name, repo: AbstractRepository):
    movie_ranks = repo.get_movie_ranks_for_director(director_name)

    return movie_ranks

def get_movies_by_rank(rank_list, repo: AbstractRepository):
    movies = repo.get_movies_by_rank(rank_list)

    # Convert Articles to dictionary form.
    movies_as_dict = movies_to_dict(movies)

    return movies_as_dict


def get_reviews_for_movie(movie_rank, repo: AbstractRepository):
    movie = repo.get_movie(movie_rank)

    if movie is None:
        raise NonExistentArticleException

    return reviews_to_dict(movie.reviews)


# ============================================
# Functions to convert model entities to dicts
# ============================================

def movie_to_dict(movie: Movie):
    movie_dict = {
        'rank': movie.rank,
        'year': movie.year,
        'title': movie.title,
        'reviews': reviews_to_dict(movie.reviews),
        'genres': genres_to_dict(movie.genres),
        'genre': movie.first_genre
    }
    return movie_dict


def movies_to_dict(movies: Iterable[Movie]):
    return [movie_to_dict(movie) for movie in movies]


def review_to_dict(review: Review):
    review_dict = {
        'username': review.user.user_name,
        'movie_rank': review.movie.rank,
        'review_text': review.review_text,
        'timestamp': review.timestamp,
        'rating': review.rating
    }
    return review_dict


def reviews_to_dict(reviews: Iterable[Review]):
    return [review_to_dict(review) for review in reviews]


def genre_to_dict(genre: Genre):
    genre_dict = {
        'name': genre.genre_name,
        'genred_movies': [movie.rank for movie in genre.genre_movie]
    }
    return genre_dict


def genres_to_dict(genres: Iterable[Genre]):
    return [genre_to_dict(genre) for genre in genres]


def actor_to_dict(actor: Actor):
    actor_dict = {
        'name': actor.actor_full_name,
        'acted_movies': [movie.rank for movie in actor.actor_movie]
    }
    return actor_dict


def actors_to_dict(actors: Iterable[Actor]):
    return [actor_to_dict(actor) for actor in actors]


def director_to_dict(director: Director):
    director_dict = {
        'name': director.director_full_name,
        'directed_movies': [movie.rank for movie in director.directed_movie]
    }
    return director_dict


def directors_to_dict(directors: Iterable[Director]):
    return [director_to_dict(director) for director in directors]

# ============================================
# Functions to convert dicts to model entities
# ============================================

def dict_to_movie(dict):
    movie = Movie(dict.title, dict.year, dict.rank)
    # Note there's no comments or tags.
    return movie