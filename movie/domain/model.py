import csv
from datetime import datetime
from typing import List, Iterable
class User:
    def __init__(self, name, password):
        if name != "" and type(name) == str:
            self.__user_name = name.strip()

        if password != "" and type(password) == str:
            self.__password = password.strip()

        self.__watched_movies = []
        self.__reviews = []
        self.__time_spent_watching_movies_minutes = 0

    def __repr__(self):
        return "<User " + self.__user_name +" "+self.__password +">"

    def __eq__(self, other):
        if isinstance(other,User):
            return self.__user_name == other.user_name
        else:
            return True

    def __lt__(self, other):
        return self.__user_name < other.user_name

    def __hash__(self):
        return hash(self.__user_name)

    def watch_movie(self, movie):
        self.__watched_movies.append(movie)
        self.__time_spent_watching_movies_minutes += movie.runtime_minutes

    def add_review(self, r):
        self.__reviews.append(r)


    @property
    def watched_movies(self):
        return self.__watched_movies

    @property
    def reviews(self) -> Iterable['Review']:
        return iter(self.__reviews)

    def add_command(self, review: 'Review'):
        self.__reviews.append(review)

    @property
    def time_spent_watching_movies_minutes(self):
        return self.__time_spent_watching_movies_minutes

    @property
    def user_name(self):
        return self.__user_name

    @property
    def password(self):
        return self.__password

class Review:
    def __init__(self, movie, text, rating, user):
        self.__movie = movie
        self.__review_text = text
        if 1 <= rating < 10:
            self.__rating = rating
        else:
            self.__rating = None
        self.__timestamp = datetime.today()
        self.__user_name = user

    def __repr__(self):
        return"<Movie " + self.__movie.title + "," + str(self.__timestamp) + '>'

    def __eq__(self, other):
        if isinstance(other,Review):
            return (self.__movie == other.movie) and (self.__review_text == other.review_text) and (self.__rating == other.rating) and (self.__timestamp == other.timestamp)
        else:
            return False

    @property
    def movie(self):
        return self.__movie

    @property
    def review_text(self):
        return self.__review_text

    @property
    def rating(self):
        return self.__rating

    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def user(self):
        return self.__user_name

class MovieFileCSVReader:
    def __init__(self, filename):
        self.__filename = filename
        self.__dataset_of_movies = [Movie("zzzzzzzz", 1900)]
        self.__dataset_of_actors = [Actor("aaaaaaaa")]
        self.__dataset_of_directors = [Director("llllll")]
        self.__dataset_of_genres = [Genre("kkkkkk")]
    def read_csv_file(self):
        csvFile = open(self.__filename, mode="r", encoding="utf-8-sig")
        reader = csv.DictReader(csvFile)
        for row in reader:
            title = row['Title'].strip()
            release_year = int(row['Year'].strip())
            actors = sorted(row['Actors'].strip().split(','))
            director = row['Director']
            genres = sorted(row['Genre'].strip().split(','))
            description = row['Description'].strip()
            runtime = int(row['Runtime (Minutes)'].strip())
            movie = Movie(title, release_year)
            movie.description = description
            movie.runtime_minutes = runtime

            new_director = Director(director)
            if new_director not in self.__dataset_of_directors:
                check_director = 0
                movie.director = new_director
                for index in range(len(self.__dataset_of_directors)):
                    if new_director < self.__dataset_of_directors[index]:
                        self.__dataset_of_directors.insert(index, new_director)
                        check_director += 1
                        break
                if check_director == 0:
                    self.__dataset_of_directors.append(new_director)
            for d in self.__dataset_of_directors:
                if d == Director("llllll"):
                    index = self.__dataset_of_directors.index(d)
                    self.__dataset_of_directors.pop(index)


            for i in actors:
                new_actor = Actor(i)
                if new_actor not in self.__dataset_of_actors:
                    movie.actors.append(new_actor)
                    check_actor = 0
                    for index in range(len(self.__dataset_of_actors)):
                        if new_actor < self.__dataset_of_actors[index]:
                            self.__dataset_of_actors.insert(index, new_actor)
                            check_actor += 1
                            break
                    if check_actor == 0:
                        self.__dataset_of_actors.append(new_actor)
            for a in self.__dataset_of_actors:
                if a == Actor("aaaaaaaa"):
                    index = self.__dataset_of_actors.index(a)
                    self.__dataset_of_actors.pop(index)

            for i in genres:
                new_genre = Genre(i)
                if new_genre not in self.__dataset_of_genres:
                    movie.genres.append(new_genre)
                    check_genre = 0
                    for index in range(len(self.__dataset_of_genres)):
                        if new_genre < self.__dataset_of_genres[index]:
                            self.__dataset_of_genres.insert(index, new_genre)
                            check_genre += 1
                            break
                    if check_genre == 0:
                        self.__dataset_of_genres.append(new_genre)
            for g in self.__dataset_of_genres:
                if g == Genre("kkkkkk"):
                    index = self.__dataset_of_genres.index(g)
                    self.__dataset_of_genres.pop(index)

            check_movie = 0
            for index in range(len(self.__dataset_of_movies)):
                if movie < self.__dataset_of_movies[index]:
                    self.__dataset_of_movies.insert(index, movie)
                    check_movie += 1
                    break
            if check_movie == 0:
                self.__dataset_of_movies.append(movie)
            for m in self.__dataset_of_movies:
                if m == Movie("zzzzzzzz", 1900):
                    index = self.__dataset_of_movies.index(m)
                    self.__dataset_of_movies.pop(index)

        csvFile.close()

    @property
    def dataset_of_directors(self):
        return self.__dataset_of_directors

    @property
    def dataset_of_actors(self):
        return self.__dataset_of_actors

    @property
    def dataset_of_genres(self):
        return self.__dataset_of_genres

    @property
    def dataset_of_movies(self):
        return self.__dataset_of_movies


class Director:
    def __init__(self, name):
        if name == "" and type(name) != str:
            self.__name = None
        else:
            self.__name = name.strip()
            self.__movie_list: List[Movie] = []

    def add_movie(self, movie:'Movie'):
        self.__movie_list.append(movie)

    @property
    def director_full_name(self) -> str:
        return self.__name

    @property
    def directed_movie(self) -> Iterable['Movie']:
        return iter(self.__movie_list)
    @property
    def number_of_actor_movie(self) -> int:
        return len(self.__movie_list)

    def is_applied_to(self, movie:'Movie') -> bool:
        return movie in self.__movie_list

    def __repr__(self):
        return '<Director ' + str(self.__name) + '>'

    def __eq__(self, other):
        return self.__name == other.__name

    def __lt__(self, other):
        return self.__name < other.__name

    def __hash__(self):
        return hash(self.__name)

class Movie:
    def __init__(self, name, year1,rank):
        if type(name) == str and name != '':
            self.__title = name.strip()
        else:
            self.__title = None

        if type(year1) == int and year1 >= 1900:
            self.__year = year1
        else:
            self.__year = None

        self.__description = ""
        self.__director = []
        self.__actors = []

        self.__genres = []
        self.__runtime_minutes = None
        self.__rank= rank
        self.__reviews = []

    def __repr__(self):
        return '<Movie ' + self.__title + ', ' + str(self.__year) + '>'

    def __eq__(self, other):
        if isinstance(other, Movie):
            return self.__title == other.__title and self.__year == other.__year
        else:
            return False

    def __lt__(self, other):
        if self.__title == other.__title:
            return self.__year < other.__year
        else:
            return self.__title < other.__title

    def __hash__(self):
        return hash((self.__title, self.__year))

    @property
    def runtime_minutes(self):
        return self.__runtime_minutes

    @property
    def title(self):
        return self.__title

    @property
    def year(self):
        return self.__year

    @property
    def description(self):
        return self.__description

    @property
    def director(self):
        return self.__director

    @property
    def actors(self) -> Iterable['Actor']:
        return iter(self.__actors)

    @property
    def number_of_actors(self):
        return len(self.__actors)

    def is_acted(self) -> bool:
        return len(self.__actors) > 0

    def is_acted_by(self, actor: 'Actor'):
        return actor in self.__actors

    @property
    def genres(self):
        return self.__genres

    @property
    def number_of_genres(self):
        return len(self.__genres)

    def is_genred_by(self, genre: 'Genre'):
        return genre in self.__genres

    def is_genred(self) -> bool:
        return len(self.__genres) > 0

    @property
    def first_genre(self):
        return self.__genres[0]

    @property
    def rank(self):
        return self.__rank

    @property
    def reviews(self) -> Iterable[Review]:
        return iter(self.__reviews)

    @property
    def number_of_reviews(self) -> int:
        return len(self.__reviews)

    @description.setter
    def description(self, value):
        if type(value) == str and value != '':
            self.__description = value.strip()

    @director.setter
    def director(self, value):
        if isinstance(value, Director):
            self.__director = value

    @runtime_minutes.setter
    def runtime_minutes(self, value):
        if type(value) == int and value > 0:
            self.__runtime_minutes = value
        else:
            raise ValueError

    def add_actor(self, actor):
        if isinstance(actor, Actor):
            if actor not in self.__actors:
                self.__actors.append(actor)

    def remove_actor(self, actor):
        if isinstance(actor, Actor):
            if actor in self.__actors:
                index = self.__actors.index(actor)
                del self.__actors[index]

    def add_genre(self, g):
        if isinstance(g, Genre):
            if g not in self.__genres:
                self.__genres.append(g)

    def remove_genre(self, g1):
        if isinstance(g1, Genre):
            if g1 in self.__genres:
                index = self.__genres.index(g1)
                del self.__genres[index]

    def add_review(self, r):
        self.__reviews.append(r)

    def add_director(self, director):
        self.__director.append(director)

class Actor:

    def __init__(self, name):
        self.__colleaguelist = []
        if name == '' or type(name) != str:
            self.__actor_name = None
        else:
            self.__actor_name = name.strip()
        self.__movie_list: List[Movie] = []

    def __repr__(self):
        return '<Actor ' + str(self.__actor_name) + '>'

    @property
    def actor_full_name(self) -> str:
        return self.__actor_name

    @property
    def actor_movie(self) -> Iterable[Movie]:
        return iter(self.__movie_list)

    @property
    def number_of_actor_movie(self):
        return len(self.__movie_list)

    def is_applied_to(self,movie:Movie) -> bool:
        return movie in self.__movie_list


    def __eq__(self, other):
        return self.__actor_name == other.__actor_name

    def __lt__(self, other):
        return self.__actor_name < other.__actor_name

    def __hash__(self):
        return hash(self.__actor_name)

    def add_actor_colleague(self, other):
        if isinstance(other, Actor):
            self.__colleaguelist.append(other)

    def check_if_this_actor_worked_with(self, other_actor):
        if isinstance(other_actor, Actor):
            if other_actor in self.__colleaguelist:
                return True
            else:
                return False

    def add_actor_movie(self,movie:Movie):
        self.__movie_list.append(movie)


class Genre:
    def __init__(self, movie_genre):
        if movie_genre == "" and type(movie_genre) != str:
            self.__genre_name = None
        else:
            self.__genre_name = movie_genre.strip()
        self.__movie_list:List[Movie] = []

    @property
    def genre_name(self) -> str:
        return self.__genre_name

    @property
    def genre_movie(self) -> Iterable[Movie]:
        return iter(self.__movie_list)

    @property
    def number_of_genre_movie(self):
        return len(self.__movie_list)

    def is_applied_to(self,movie:Movie)->bool:
        return movie in self.__movie_list

    def add_genre_movie(self, movie:Movie):
        self.__movie_list.append(movie)

    def __repr__(self):
        return '<Genre ' + str(self.__genre_name) + '>'

    def __eq__(self, other):
        return self.__genre_name == other.__genre_name

    def __lt__(self, other):
        return self.__genre_name < other.__genre_name

    def __hash__(self):
        return hash(self.__genre_name)








class WatchList:
    pass
class ModelException(Exception):
    pass

def make_review(review_text: str, user: User, movie: Movie,review_num: int):
    review = Review(movie, review_text,review_num, user)
    user.add_review(review)
    movie.add_review(review)
    return review


def make_genre_association(movie:Movie, genre:Genre):
    if genre.is_applied_to(movie):
        raise ModelException(f'Tag {movie.title} already applied to Movie "{movie.title}"')

    movie.add_genre(genre)
    genre.add_genre_movie(movie)


def make_actor_association(movie:Movie,actor:Actor):
    if actor.is_applied_to(movie):
        raise ModelException(f'Tag {movie.title} already applied to Movie "{movie.title}"')

    movie.add_actor(actor)
    actor.add_actor_movie(movie)


def make_director_association(movie:Movie,director:Director):
    if director.is_applied_to(movie):
        raise ModelException(f'Tag {movie.title} already applied to Movie "{movie.title}"')

    movie.add_director(director)
    director.add_movie(movie)

