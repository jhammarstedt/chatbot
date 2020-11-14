# Here is where the NLP magic will happen!
import json
import tmdbsimple as tm


def start_api():
    with open('tokens.json') as f:
        data = json.load(f)

    api = data['tokens'][0]['TMDB']
    tm.API_KEY = api


def get_data():
    """The basic language logic for now will just be to map keywords"""
    with open('keyword_mapper.json') as f:
        data = json.load(f)
    keyword_genres = data['genre']
    keyword_popularity = data['popularity']
    keyword_countries = data['countries']
    return keyword_genres, keyword_countries, keyword_popularity


class Dialog():
    """
    This class will keep somewhat track of the dialog to know what movies to recommend
    Will hold: keywords, current selection, (maybe past selection too)
    functions:
    - incomming message : something that handles the incoming message and sorts the keywords
    - process_message: Takes the current lists and applies the keywords

    """

    def __init__(self):
        self.keywords = {'genre': None,
                         'actor': None,  # is there even
                         'country': None,
                         'rating_threshold': None,
                         'popular': False}
        self.next_action = None
        self.current_movies = []  # list of current relevant movies
        self.kw_genres, self.kw_countries, self.kw_pop = get_data()
        self.current_chat = []

    def get_popular(self, pages=5):
        if len(self.current_movies) == 0:  # if we don't have any previous recs
            d = tm.Discover()  # Setting discovery mode for the API
            movies = []
            a = []
            for i in range(1, pages):
                movies.append(
                    d.movie(sort_by=['vote_count.desc'], page=i)['results'])  # get 5 pages with most vote counts
            flatten = [item for sublist in movies for item in
                       sublist]  # Since we get a list of lists of dicts we have to flatten it to one list of dicts
            flatten = sorted(flatten, key=lambda k: k['vote_average'], reverse=True)  # sort them by vote_average
            self.current_movies = flatten
        else:  # if we just want to sort the current selection by popularity
            self.current_movies = sorted(self.current_movies, key=lambda k: k['vote_average'],
                                         reverse=True)  # sort them by vote_average

    def filter_by_genre(self, pages=5):
        if len(self.current_movies) == 0:  # if this was our first request to filter on
            movies = []
            for i in range(1, pages):
                movies.append(tm.Genres(
                    self.kw_genres[self.keywords['genre']], page=i)['results'])  # get 5 pages with most vote counts
            flatten = [item for sublist in movies for item in sublist]
            self.current_movies = flatten
        else:
            # filter out by genre and update our selection, will probably be generalized later
            selection = []
            for movie in self.current_movies:  # go through all movies
                if self.kw_genres[self.keywords['genre']] in movie[
                    'genre_ids']:  # check if the genre id that we want is in the current movie
                    selection.append(movie)

            self.current_movies = selection  # update our selections

    def process_message_txt(self, msg: str):
        """Very simply word logic for now"""
        split = msg.split(' ')
        for word in split:
            if word in self.kw_pop:
                self.keywords['popular'] = True
                self.next_action = 'popular'
            elif word in list(self.kw_genres.keys):
                self.keywords['genre'] = [word, self.kw_genres[word]]
                self.next_action = 'genre'
            elif word in self.kw_countries:
                self.keywords['country'] = word
                self.next_action = 'country'

    def act_on_message(self):

        if self.next_action == 'popular':  # filter on popular movies
            self.get_popular()  # sort or create a list of popular movies
        elif self.next_action == 'genre':
            self.filter_by_genre()  # filter or create a list based on genre