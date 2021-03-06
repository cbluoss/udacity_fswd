from fresh_tomatoes import *


class Movie():
    """A dict would work just fine for this task, but well, 
    to lazy to rewrite create_movie_tiles_content.
    And even more important: not very pythonic
    """

    def __init__(self, title, image_url, yt_url):
        #This function is 7 lines in total. 
        #Would not write any comments below 10 lines
        #or lots of magic.
        self.title = title
        self.poster_image_url = image_url
        self.trailer_youtube_url = yt_url


if __name__ == '__main__':
    """
    Those URLS are pretty and to quote PEP8:
    'But most importantly: know when to be inconsistent -- 
     sometimes the style guide just doesn't apply. 
     When in doubt, use your best judgment.
    """
    movies = [Movie("Blade Runner",
                    "http://www.vangelishistory.com/brposinternational.jpg-for-web-large.jpg", 
                    "https://www.youtube.com/watch?v=eogpIG53Cis"),
              Movie("Indiana Jones", 
                    "http://www.impawards.com/1984/posters/indiana_jones_and_the_temple_of_doom_ver3.jpg",
                    "https://www.youtube.com/watch?v=HqOSLZl9GUo"),
              Movie("Matrix", 
                    "https://images-na.ssl-images-amazon.com/images/M/MV5BMDMyMmQ5YzgtYWMxOC00OTU0LWIwZjEtZWUwYTY5MjVkZjhhXkEyXkFqcGdeQXVyNDYyMDk5MTU@._V1_SY1000_CR0,0,723,1000_AL_.jpg", 
                    "https://www.youtube.com/watch?v=m8e-FF8MsqU")]
    open_movies_page(movies)
