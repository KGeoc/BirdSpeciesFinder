import datetime as dt
import re
import time

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


bird_fams = []
bird_specs = []


def get_bird_families():
    global bird_fams
    bird_fams = bird_species.find({}, {"_id": 0, "common_family": 1}).distinct('common_family')
    global bird_specs
    bird_specs = list(bird_species.find({}, {"_id": 0, "common_family": 1, 'common_name': 1}))

found_matches=0

def find_bird_from_sentence(x):

    for fams in bird_fams:
        if re.search(rf"\W{fams}\W", x, flags=re.IGNORECASE):

            copy_of_bird_specs = bird_specs
            new_list = list(filter(lambda a: fams in a['common_family'], copy_of_bird_specs))
            found=False
            for entries in new_list:
                if re.search(rf"(?<!\w){entries['common_name']}(?!=\w)", x, flags=re.IGNORECASE):
                    global found_matches
                    found_matches+=1
                    found=True
                    #print(x)
                    #print(entries)
                    break
            if found==False:
                print("not species\n",x)
            break


def get_bird_posts():
    bird_posts = list(my_col.find({}, {"_id": 0, "title": 1}))
    print(len(bird_posts))
    for x in bird_posts:
        find_bird_from_sentence(x["title"])
    print(found_matches)

    # print(re.findall(r"(?=(" + '|'.join(qwer) + r"))", x))


if __name__ == '__main__':
    print('')
    # create_post_db()
    # create_species_db("birdlist.csv")
    #obtain_new_info()
    get_bird_families()
    get_bird_posts()
    print("found ",found_matches)
    find_bird_from_sentence("this is a Yellowthroat")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
