from datetime import date

from movie.domain.model import User, Movie, Actor, Genre, make_genre_association, make_actor_association, ModelException, make_review

import pytest


@pytest.fixture()
def movie():
    return Movie("Prometheus", 2012, 2)


@pytest.fixture()
def user():
    return User('dbowie', '1234567890')


@pytest.fixture()
def actor():
    return Actor('Noomi Rapace')


@pytest.fixture()
def genre():
    return Genre('Adventure')


def test_user_construction(user):
    assert user.user_name == 'dbowie'
    assert user.password == '1234567890'
    assert repr(user) == '<User dbowie 1234567890>'

    for reviews in user.reviews:
        # User should have an empty list of Comments after construction.
        assert False


def test_movie_construction(movie):
    assert movie.title == "Prometheus"
    assert movie.year == 2012
    assert movie.number_of_reviews == 0
    assert movie.number_of_genres == 0
    assert movie.number_of_actors == 0

    assert repr(movie) == '<Movie Prometheus, 2012>'


def test_movie_less_than_operator():
    movie_1 = Movie("Prometheus", 2012, 2)

    movie_2 = Movie("Split", 2016, 3)

    assert movie_1 < movie_2


def test_actor_construction(actor):
    assert actor.actor_full_name == 'Noomi Rapace'

    for movie in actor.actor_movie:
        assert False

    assert not actor.is_applied_to(Movie(None, None, 0))


def test_genre_construction(genre):
    assert genre.genre_name == 'Adventure'

    for movie in genre.genre_movie:
        assert False

    assert not genre.is_applied_to(Movie(None, None, 0))


def test_make_review_establishes_relationships(movie, user):
    review_text = 'Movie World!'
    review = make_review(review_text, user, movie, 23)

    # Check that the User object knows about the Comment.
    assert review in user.reviews

    # Check that the Comment knows about the User.
    assert review.user is user

    # Check that Article knows about the Comment.
    assert review in movie.reviews

    # Check that the Comment knows about the Article.
    assert review.movie is movie


def test_make_genre_associations(movie, genre, actor):
    make_genre_association(movie, genre)
    make_actor_association(movie, actor)
    # Check that the Article knows about the Tag.
    assert movie.is_acted()
    assert movie.is_acted_by(actor)
    assert movie.is_genred()
    assert movie.is_genred_by(genre)
    # check that the Tag knows about the Article.
    assert actor.is_applied_to(movie)
    assert movie in actor.actor_movie
    assert genre.is_applied_to(movie)
    assert movie in genre.genre_movie


def test_make_genre_associations_with_movie_already_tagged(movie, genre):
    make_genre_association(movie, genre)

    with pytest.raises(ModelException):
        make_genre_association(movie, genre)
