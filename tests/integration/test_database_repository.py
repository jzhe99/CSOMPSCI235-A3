from datetime import date, datetime

import pytest

from movie.adapters.database_repository import SqlAlchemyRepository
from movie.domain.model import User, Movie, Genre, Review, make_review
from movie.adapters.repository import RepositoryException

def test_repository_can_add_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User('Dave', '123456789')
    repo.add_user(user)

    repo.add_user(User('Martin', '123456789'))

    user2 = repo.get_user('Dave')

    assert user2 == user and user2 is user

def test_repository_can_retrieve_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')

def test_repository_does_not_retrieve_a_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('prince')
    assert user is None

def test_repository_can_retrieve_movie_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_movies = repo.get_number_of_movies()

    # Check that the query returned 177 Articles.
    assert number_of_movies == 177

def test_repository_can_add_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_movies = repo.get_number_of_movies()

    new_movie_rank = number_of_movies + 1

    movie = Movie("Cool World",2015, new_movie_rank)
    repo.add_movie(movie)

    assert repo.get_movie(new_movie_rank) == movie

def test_repository_can_retrieve_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(1)

    # Check that the Article has the expected title.
    assert movie.title == 'Guardians of the Galaxy'

    # Check that the Article is commented as expected.
    review_one = [review for review in movie.reviews if review.review_text == 'Oh no, COVID-19 has hit New Zealand'][
        0]
    review_two = [review for review in movie.reviews if review.review_text == 'Yeah Freddie, bad news'][0]

    assert review_one.user.username == 'fmercury'
    assert review_two.user.username == "thorke"

    # Check that the Article is tagged as expected.
    assert movie.is_genred_by(Genre('Health'))
    assert movie.is_genred_by(Genre('New Zealand'))

def test_repository_does_not_retrieve_a_non_existent_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(201)
    assert movie is None

def test_repository_can_retrieve_movies_by_year(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_year(2012)

    # Check that the query returned 3 Articles.
    assert len(movies) == 1

    # these articles are no jokes...
    movies = repo.get_movies_by_year(2016)

    # Check that the query returned 5 Articles.
    assert len(movies) == 3

def test_repository_does_not_retrieve_a_movie_when_there_are_no_movies_for_a_given_year(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    articles = repo.get_movies_by_year(2000)
    assert len(articles) == 0

def test_repository_can_retrieve_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genres = repo.get_genre()

    assert len(genres) == 10

    genre_one = [genre for genre in genres if genre.genre_name == 'Action'][0]
    genre_two = [genre for genre in genres if genre.genre_name == 'Adventure'][0]
    genre_three = [genre for genre in genres if genre.genre_name == 'Sci-Fi'][0]
    genre_four = [genre for genre in genres if genre.genre_name == 'Mystery'][0]

    assert genre_one.number_of_genre_movie == 2
    assert genre_two.number_of_genre_movie == 3
    assert genre_three.number_of_genre_movie == 2
    assert genre_four.number_of_genre_movie == 1

def test_repository_can_get_first_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_first_movie()
    assert movie.title == 'Guardians of the Galaxy'

def test_repository_can_get_last_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_last_movie()
    assert movie.title == 'Suicide Squad'

def test_repository_can_get_movies_by_ranks(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_rank([2, 1, 3])

    assert len(movies) == 3
    assert movies[
               0].title == 'Prometheus'
    assert movies[1].title == "Guardians of the Galaxy"
    assert movies[2].title == 'Split'

def test_repository_does_not_retrieve_movie_for_non_existent_rank(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_rank([2, 209])

    assert len(movies) == 1
    assert movies[
               0].title == 'Prometheus'

def test_repository_returns_an_empty_list_for_non_existent_ranks(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_rank([0, 199])

    assert len(movies) == 0

def test_repository_returns_movie_ranks_for_existing_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie_ranks = repo.get_movie_ranks_for_genre('Mystery')

    assert movie_ranks == [2]

def test_repository_returns_an_empty_list_for_non_existent_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie_ranks = repo.get_movie_ranks_for_genre('United States')

    assert len(movie_ranks) == 0


def test_repository_returns_year_of_previous_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(2)
    previous_year = repo.get_year_of_previous_movie(movie)

    assert previous_year == 2012


def test_repository_returns_none_when_there_are_no_previous_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(1)
    previous_year = repo.get_year_of_previous_movie(movie)

    assert previous_year is None


def test_repository_returns_year_of_next_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(2)
    next_year = repo.get_year_of_next_movie(movie)

    assert next_year == 2016


def test_repository_returns_none_when_there_are_no_subsequent_movies(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(5)
    next_year = repo.get_year_of_next_movie(movie)

    assert next_year is None


def test_repository_can_add_a_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genre = Genre('Motoring')
    repo.add_genre(genre)

    assert genre in repo.get_genre()


def test_repository_can_add_a_reviews(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('thorke')
    movie = repo.get_movie(2)
    review = make_review("Trump's onto it!", user, movie)

    repo.add_review(review)

    assert review in repo.get_reviews()


def test_repository_does_not_add_a_review_without_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(2)
    review = Review(movie, "Trump's onto it!", None, None)

    with pytest.raises(RepositoryException):
        repo.add_review(review)


def test_repository_can_retrieve_reviews(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    assert len(repo.get_reviews()) == 3


def make_movie(new_movie_year):
    movie = Movie("Cool Word",2015,6)
    return movie

def test_can_retrieve_a_movie_and_add_a_review_to_it(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    # Fetch Article and User.
    movie = repo.get_movie(2)
    author = repo.get_user('thorke')

    # Create a new Comment, connecting it to the Article and User.
    review = make_review('First death in Australia', author, movie)

    movie_fetched = repo.get_movie(2)
    author_fetched = repo.get_user('thorke')

    assert review in movie_fetched.reviews
    assert review in author_fetched.reviews

