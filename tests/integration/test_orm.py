import pytest

import datetime

from sqlalchemy.exc import IntegrityError

from movie.domain.model import User, Movie, Review, Genre, make_review, make_genre_association

movie_year = 2012

def insert_user(empty_session, values=None):
    new_name = "Andrew"
    new_password = "1234"

    if values is not None:
        new_name = values[0]
        new_password = values[1]

    empty_session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                          {'username': new_name, 'password': new_password})
    row = empty_session.execute('SELECT id from users where username = :username',
                                {'username': new_name}).fetchone()
    return row[0]

def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                              {'username': value[0], 'password': value[1]})
    rows = list(empty_session.execute('SELECT id from users'))
    keys = tuple(row[0] for row in rows)
    return keys

def insert_movie(empty_session):
    empty_session.execute(
        'INSERT INTO ,movies (rank, year, title, director, genres, actors) VALUES '
        '(2,2012, "Prometheus", None, None, None)' )
    row = empty_session.execute('SELECT rank from movies').fetchone()
    return row[0]


def insert_genres(empty_session):
    empty_session.execute(
        'INSERT INTO genres (name) VALUES ("News"), ("New Zealand")'
    )
    rows = list(empty_session.execute('SELECT id from genres'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_movie_genre_associations(empty_session, movie_key, genre_keys):
    stmt = 'INSERT INTO article_tags (movie_rank, genre_id) VALUES (:movie_rank, :genre_id)'
    for genre_key in genre_keys:
        empty_session.execute(stmt, {'movie_id': movie_key, 'genre_id': genre_key})


def insert_commented_movie(empty_session):
    movie_key = insert_movie(empty_session)
    user_key = insert_user(empty_session)

    timestamp_1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timestamp_2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    empty_session.execute(
        'INSERT INTO reviews (user_id, movie_rank, review, timestamp) VALUES '
        '(:user_id, :movie_id, "Comment 1", :timestamp_1),'
        '(:user_id, :movie_id, "Comment 2", :timestamp_2)',
        {'user_id': user_key, 'movie_id': movie_key, 'timestamp_1': timestamp_1, 'timestamp_2': timestamp_2}
    )

    row = empty_session.execute('SELECT rank from movies').fetchone()
    return row[0]


def make_movie():
    movie = Movie('Prometheus',2012,2)
    return movie


def make_user():
    user = User("Andrew", "111")
    return user


def make_genre():
    genre = Genre("Adventure,Mystery,Sci-Fi")
    return genre


def test_loading_of_users(empty_session):
    users = list()
    users.append(("Andrew", "1234"))
    users.append(("Cindy", "1111"))
    insert_users(empty_session, users)

    expected = [
        User("Andrew", "1234"),
        User("Cindy", "999")
    ]
    assert empty_session.query(User).all() == expected

def test_saving_of_users(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT username, password FROM users'))
    assert rows == [("Andrew", "111")]


def test_saving_of_users_with_common_username(empty_session):
    insert_user(empty_session, ("Andrew", "1234"))
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User("Andrew", "111")
        empty_session.add(user)
        empty_session.commit()


def test_loading_of_movie(empty_session):
    movie_key = insert_movie(empty_session)
    expected_movie = make_movie()
    fetched_movie = empty_session.query(Movie).one()

    assert expected_movie == fetched_movie
    assert movie_key == fetched_movie.rank


def test_loading_of_genred_movie(empty_session):
    movie_key = insert_movie(empty_session)
    genre_keys = insert_genres(empty_session)
    insert_movie_genre_associations(empty_session, movie_key, genre_keys)

    movie = empty_session.query(Movie).get(movie_key)
    genres = [empty_session.query(Genre).get(key) for key in genre_keys]

    for genre in genres:
        assert movie.is_tagged_by(genre)
        assert genre.is_applied_to(movie)


def test_loading_of_commented_movie(empty_session):
    insert_commented_movie(empty_session)

    rows = empty_session.query(Movie).all()
    movie = rows[0]

    assert len(movie.reviews) == 2

    for review in movie.reviews:
        assert review.movie is movie


def test_saving_of_reviews(empty_session):
    movie_key = insert_movie(empty_session)
    user_key = insert_user(empty_session, ("Andrew", "1234"))
    rows = empty_session.query(Movie).all()
    movie = rows[0]
    user = empty_session.query(User).filter(User.user_name == "Andrew").one()

    # Create a new Comment that is bidirectionally linked with the User and Article.
    review_text = "Some comment text."
    review = make_review(review_text, user, movie)

    # Note: if the bidirectional links between the new Comment and the User and
    # Article objects hadn't been established in memory, they would exist following
    # committing the addition of the Comment to the database.
    empty_session.add(review)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_id, movie_id, review FROM reviews'))

    assert rows == [(user_key, movie_key, review_text)]


def test_saving_of_movie(empty_session):
    movie = make_movie()
    empty_session.add(movie)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT year, title, director, genres, actors FROM movies'))
    #year = movie_year
    assert rows == [(2012,"Prometheus","Ridley Scott","Adventure,Mystery,Sci-Fi","Noomi Rapace, Logan Marshall-Green, Michael Fassbender, Charlize Theron")]


def test_saving_genred_movie(empty_session):
    movie = make_movie()
    genre = make_genre()

    # Establish the bidirectional relationship between the Article and the Tag.
    make_genre_association(movie, genre)

    # Persist the Article (and Tag).
    # Note: it doesn't matter whether we add the Tag or the Article. They are connected
    # bidirectionally, so persisting either one will persist the other.
    empty_session.add(movie)
    empty_session.commit()

    # Test test_saving_of_article() checks for insertion into the articles table.
    rows = list(empty_session.execute('SELECT rank FROM movies'))
    movie_key = rows[0][0]

    # Check that the tags table has a new record.
    rows = list(empty_session.execute('SELECT id, name FROM genres'))
    genre_key = rows[0][0]
    assert rows[0][1] == "Adventure,Mystery,Sci-Fi"

    # Check that the article_tags table has a new record.
    rows = list(empty_session.execute('SELECT movie_id, genre_id from movie_genres'))
    movie_foreign_key = rows[0][0]
    genre_foreign_key = rows[0][1]

    assert movie_key == movie_foreign_key
    assert genre_key == genre_foreign_key


def test_save_commented_movie(empty_session):
    # Create Article User objects.
    movie = make_movie()
    user = make_user()

    # Create a new Comment that is bidirectionally linked with the User and Article.
    review_text = "Some comment text."
    review = make_review(review_text, user, movie)

    # Save the new Article.
    empty_session.add(movie)
    empty_session.commit()

    # Test test_saving_of_article() checks for insertion into the articles table.
    rows = list(empty_session.execute('SELECT rank FROM movies'))
    movie_key = rows[0][0]

    # Test test_saving_of_users() checks for insertion into the users table.
    rows = list(empty_session.execute('SELECT id FROM users'))
    user_key = rows[0][0]

    # Check that the comments table has a new record that links to the articles and users
    # tables.
    rows = list(empty_session.execute('SELECT user_id, movie_id, review FROM reviews'))
    assert rows == [(user_key, movie_key, review_text)]