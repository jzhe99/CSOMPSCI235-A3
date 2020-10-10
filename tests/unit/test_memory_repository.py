from datetime import date, datetime
from typing import List

import pytest

from movie.domain.model import User, Movie, Actor,Genre, Review, make_review
from movie.adapters.repository import RepositoryException


def test_repository_can_add_a_user(in_memory_repo):
    user = User('Dave', '123456789')
    in_memory_repo.add_user(user)

    assert in_memory_repo.get_user('Dave') is user


def test_repository_can_retrieve_a_user(in_memory_repo):
    user = in_memory_repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_movie_count(in_memory_repo):
    number_of_movie = in_memory_repo.get_number_of_movies()

    # Check that the query returned 6 Articles.
    assert number_of_movie == 1000


def test_repository_can_add_movie(in_memory_repo):
    movie = Movie(name='Prometheus', year1=2012, rank=2)
    in_memory_repo.add_movie(movie)

    assert in_memory_repo.get_movie(2) is movie


def test_repository_can_retrieve_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(1)

    # Check that the Article has the expected title.
    assert movie.title == 'Guardians of the Galaxy'

    # Check that the Article is commented as expected.
    review_one = [review for review in movie.reviews if review.review_text == 'Oh no, COVID-19 has hit New Zealand'][0]
    review_two = [review for review in movie.reviews if review.review_text == 'Yeah Freddie, bad news'][0]

    assert review_one.user.user_name == 'fmercury'
    assert review_two.user.user_name == "thorke"

    # Check that the Article is tagged as expected.
    assert movie.is_genred_by(Genre('Action'))
    assert movie.is_genred_by(Genre('Adventure'))
    assert movie.is_genred_by(Genre('Sci-Fi'))
    assert movie.is_acted_by(Actor('Chris Pratt'))
    assert movie.is_acted_by(Actor('Vin Diesel'))
    assert movie.is_acted_by(Actor('Bradley Cooper'))
    assert movie.is_acted_by(Actor('Zoe Saldana'))


def test_repository_does_not_retrieve_a_non_existent_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(1001)
    assert movie is None


def test_repository_can_retrieve_movie_by_year(in_memory_repo):
    movies = in_memory_repo.get_movies_by_year(2012)

    # Check that the query returned 3 Articles.
    assert len(movies) == 64


def test_repository_does_not_retrieve_a_movie_when_there_are_no_movies_for_a_given_year(in_memory_repo):
    movies = in_memory_repo.get_movies_by_year(2020)
    assert len(movies) == 0


def test_repository_can_retrieve_genres(in_memory_repo):
    genres: List[Genre] = in_memory_repo.get_genre()

    assert len(genres) == 20

    genre_one = [genre for genre in genres if genre.genre_name == 'Adventure'][0]
    genre_two = [genre for genre in genres if genre.genre_name == 'Mystery'][0]
    genre_three = [genre for genre in genres if genre.genre_name == 'Sci-Fi'][0]

    assert genre_one.number_of_genre_movie == 259
    assert genre_two.number_of_genre_movie == 106
    assert genre_three.number_of_genre_movie == 120


def test_repository_can_get_first_movie(in_memory_repo):
    movie = in_memory_repo.get_first_movie()
    assert movie.title == '(500) Days of Summer'


def test_repository_can_get_last_movie(in_memory_repo):
    movie = in_memory_repo.get_last_movie()
    assert movie.title == 'Zootopia'


def test_repository_can_get_movie_by_ranks(in_memory_repo):
    movies = in_memory_repo.get_movies_by_rank([2, 5])

    assert len(movies) == 2
    assert movies[0].title == 'Prometheus'
    assert movies[1].title == "Suicide Squad"


def test_repository_does_not_retrieve_movie_for_non_existent_rank(in_memory_repo):
    movies = in_memory_repo.get_movies_by_rank([2, 9])

    assert len(movies) == 2
    assert movies[0].title == 'Prometheus'


def test_repository_returns_an_empty_list_for_non_existent_ranks(in_memory_repo):
    movies = in_memory_repo.get_movies_by_rank([0, 9])

    assert len(movies) == 1


def test_repository_returns_movie_ranks_for_existing_genre(in_memory_repo):
    movies_genres = in_memory_repo.get_movie_ranks_for_genre('Horror')

    assert movies_genres == [3, 23, 28, 35, 43, 57, 62, 98, 111, 117, 119, 133, 155, 156, 173, 179, 182, 188, 194, 202, 207, 210, 219, 223, 230, 238, 255, 259, 266, 270, 291, 303, 313, 318, 319, 327, 329, 336, 349, 362, 364, 381, 383, 402, 416, 423, 429, 430, 433, 446, 450, 453, 462, 478, 491, 493, 495, 496, 514, 528, 532, 562, 563, 596, 622, 623, 624, 633, 634, 639, 645, 648, 651, 653, 676, 684, 691, 701, 706, 718, 724, 726, 737, 749, 752, 765, 777, 801, 805, 812, 813, 819, 820, 826, 827, 829, 859, 866, 876, 877, 889, 896, 909, 911, 916, 918, 922, 935, 937, 941, 957, 964, 969, 971, 974, 987, 989, 994, 997]


def test_repository_returns_an_empty_list_for_non_existent_genre(in_memory_repo):
    movie_ranks = in_memory_repo.get_movie_ranks_for_genre('Experimental')

    assert len(movie_ranks) == 0


def test_repository_returns_year_of_previous_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(6)
    previous_year = in_memory_repo.get_year_of_previous_movie(movie)

    assert previous_year == 2015


def test_repository_returns_none_when_there_are_no_previous_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(65)
    previous_year = in_memory_repo.get_year_of_previous_movie(movie)

    assert previous_year is None


def test_repository_returns_date_of_next_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(2)
    next_year = in_memory_repo.get_year_of_next_movie(movie)

    assert next_year == 2013


def test_repository_returns_none_when_there_are_no_subsequent_movies(in_memory_repo):
    movie = in_memory_repo.get_movie(6)
    next_year = in_memory_repo.get_year_of_next_movie(movie)

    assert next_year is None


def test_repository_can_add_a_genre(in_memory_repo):
    genre = Genre('Crime')
    in_memory_repo.add_genre(genre)

    assert genre in in_memory_repo.get_genre()


def test_repository_can_add_a_review(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    movie = in_memory_repo.get_movie(2)
    review = make_review("Trump's onto it!", user, movie, 4)

    in_memory_repo.add_review(review)

    assert review in in_memory_repo.get_reviews()


def test_repository_does_not_add_a_review_without_a_user(in_memory_repo):
    movie = in_memory_repo.get_movie(2)
    review = Review( movie, "Trump's onto it!", 5, None)

    with pytest.raises(RepositoryException):
        in_memory_repo.add_review(review)


def test_repository_does_not_add_a_review_without_an_movie_properly_attached(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    movie = in_memory_repo.get_movie(2)
    review = Review( movie, "Trump's onto it!", 5, None)

    user.add_review(review)

    with pytest.raises(RepositoryException):
        # Exception expected because the Article doesn't refer to the Comment.
        in_memory_repo.add_review(review)


def test_repository_can_retrieve_reviews(in_memory_repo):
    assert len(in_memory_repo.get_reviews()) == 2


def test_repository_can_get_movie_by_director(in_memory_repo):
    movies = in_memory_repo.get_movies_by_director('Yimou Zhang')

    assert len(movies) == 1
    assert movies[0].title == 'The Great Wall'


def test_repository_returns_an_empty_list_for_non_existent_director(in_memory_repo):
    movies = in_memory_repo.get_movies_by_director('Chun David')

    assert len(movies) == 0
