import datetime as dt
import sys

from TrieNode import TrieNode as Bird_Trie
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

Bird_Trie = Bird_Trie()


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
    added_posts = 0
    submissions = reddit.subreddit(sub_to_search).new(limit=500)

    for posts in submissions:
        if my_col.find_one({"post_id": posts.id}):
            continue
        else:
            try:
                my_col.insert_one({
                    "post_id": posts.id,
                    "username": posts.author.name,
                    "date": posts.created_utc,
                    "title": posts.title,
                    "subreddit": posts.subreddit.display_name,
                    "post_searched": False
                })
            except AttributeError as ex:
                my_col.insert_one({
                    "post_id": posts.id,
                    "username": "None",
                    "date": posts.created_utc,
                    "title": posts.title,
                    "subreddit": posts.subreddit.display_name,
                    "post_searched": False
                })
            added_posts += 1
    return added_posts


bird_fams = []
bird_specs = []


def get_bird_families():
    global bird_fams
    bird_fams = bird_species.find({}, {"_id": 0, "common_family": 1}).distinct('common_family')
    global bird_specs
    bird_specs = list(bird_species.find({}, {"_id": 0, "common_family": 1, 'common_name': 1}))


num_matches = 0


def make_trie():
    # bird_trie=TrieNode
    Bird_Trie.add_word("asdf")
    for common_birds in bird_specs:
        Bird_Trie.add_word(re.sub('[^a-zA-Z0-9]', '', common_birds['common_name']).lower())


def find_bird_from_sentence(x):
    for identified_family in bird_fams:
        found_bird = re.search(rf"(?:\W|^)({identified_family})(?:\W|$|s|es)", x, flags=re.IGNORECASE)
        if found_bird:
            new_word = re.sub('[^a-zA-Z0-9]', '', x[0:found_bird.span()[1]]).lower()

            for position in range(0, len(new_word) - 1):
                list_trie_results = Bird_Trie.find_word(new_word[position:])

                if list_trie_results:
                    for found in list_trie_results:
                        global num_matches
                        num_matches += 1
                        result = bird_species.find_one(
                            {"common_family": identified_family, "concat_name": new_word[position:position + found]},
                            {"_id": 0, "common_name": 1})
                        if result is not None:
                            return {'family': identified_family, 'species': result["common_name"]}
            return {'family': identified_family}

    return False


def get_bird_posts():
    bird_posts = list(my_col.find({"processed": { "$exists" : False }}, {"_id": 0, "title": 1, "post_id": 1})
                      .sort('date', pymongo.DESCENDING))

    method_time = 0

    for x in bird_posts:
        # print(x)
        tic = time.perf_counter()
        found_bird = find_bird_from_sentence(x["title"])
        if found_bird is not False:
            if 'species' not in found_bird:
                insert_results(x["post_id"], found_bird['family'], None,True)
            else:
                insert_results(x["post_id"], found_bird['family'], found_bird['species'],True)
        else:
            insert_negative(x["post_id"],True)
            # print(found_bird)
        toc = time.perf_counter()
        method_time += toc - tic

    print("Search time\t", method_time)
    print(len(bird_posts), "posts")
    print(num_matches, "matches")
    # current result is method B is faster and more accurate.
    # Method A	 69.55064550000003 Method B	 67.19713309999995
    # 1205 posts
    # 438 results A
    # 516 results B

    # print(re.findall(r"(?=(" + '|'.join(qwer) + r"))", x))


# placeholder for if bird is found
def insert_results(url, family, species,automated):
    # pseudo update url with family and species if provided
    # add field automated and make true

    if species is None:
        my_col.update_one({"post_id": url},
                          {"$set": {
                              "family_name": family,
                              "species": None,
                              "automated": automated,
                              "processed":True
                          }})
    else:
        my_col.update_one({"post_id": url},
                          {"$set": {
                              "family_name": family,
                              "species": species,
                              "automated": automated,
                              "processed":True
                          }})


# placeholder for if bird was not found
def insert_negative(url, automated):
    my_col.update_one({"post_id": url},
                      {"$set": {
                          "family_name": None,
                          "species": None,
                          "automated": automated,
                          "processed": True
                      }})


def test_results(x):
    print(find_bird_from_sentence(x))


if __name__ == '__main__':
    print('')
    # create_post_db()
    # create_species_db("birdlist.csv")
    print(obtain_new_info())

    get_bird_families()
    make_trie()
    # test_results("Turkey vulture")
    # turkey vulture will not be found due to the first word being found being turkey.

    # print(len(bird_fams))
    get_bird_posts()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
