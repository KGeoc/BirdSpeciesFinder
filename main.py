import datetime as dt
import re
import praw
import pymongo
import credentials
import birdimport


# TODO implement a search that will first search for bird as species, robin, hummingbird, heron.
#  Then search for subspecies, great blue heron, green heron.

reddit = praw.Reddit(username=credentials.username,
                     password=credentials.password,
                     client_id=credentials.client_id,
                     client_secret=credentials.client_secret,
                     user_agent=credentials.user_agent)


def login_reddit():
    print(f'you are logged in as {reddit.user.me()}')


my_client = pymongo.MongoClient("mongodb://localhost:27017/")

my_db = my_client["BirdInfo"]

my_col = my_db["RedditBirdPosts"]
bird_species = my_db["BirdSpecies"]


def create_post_db():
    my_col.create_index("post_id", unique=True)


# post database should have url, poster, title, date

# birds should have Family, genus, species, common name, scientific name

def create_species_db(file_name):
    birdimport.file_import(file_name)


sub_to_search = "birdpics"


def obtain_new_info():
    submissions = reddit.subreddit(sub_to_search).new(limit=500)

    for posts in submissions:
        if my_col.find_one({"post_id": posts.id}):
            continue
        else:
            my_col.insert_one({
                "post_id": posts.id,
                "username": posts.author.name,
                "date": posts.created_utc,
                "title": posts.title,
                "subreddit": posts.subreddit.display_name,
                "post_searched": False
            })


def get_bird_families():
    return bird_species.find().distinct('common_family')


def find_bird_from_sentence(x):
    for fams in bird_species.find().distinct('common_family'):
        print( re.search(rf"{fams}",x,flags=re.IGNORECASE))

    qwer=bird_species.find().distinct('common_family')


    #print(re.findall(r"(?=(" + '|'.join(qwer) + r"))", x))

if __name__ == '__main__':
    print('')
    # create_post_db()
    # create_species_db("birdlist.csv")
    # obtain_new_info()
    get_bird_families()
    find_bird_from_sentence("this is a Yellowthroat")
    test()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
