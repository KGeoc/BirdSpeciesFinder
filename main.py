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


found_matches_A = 0
found_matches_B = 0


def make_trie():
    # bird_trie=TrieNode
    Bird_Trie.add_word("asdf")
    for common_birds in bird_specs:
        Bird_Trie.add_word(re.sub('[^a-zA-Z0-9]', '', common_birds['common_name']).lower())
    #print(Bird_Trie.find_word('lesserrhea'))


def new_find_bird_from_sentence(x):
    if "sidhe" in x:
        print("FDGSDFG")
    for fams in bird_fams:
        found_bird = re.search(rf"(?:\W|^)({fams})(?:\W|$)", x, flags=re.IGNORECASE)
        if found_bird:
            new_word = re.sub('[^a-zA-Z0-9]', '', x[0:found_bird.span()[1]]).lower()
            for position in range(0, found_bird.span()[0]):
                if new_word == 'afuzzynewbarredowlet':
                    print("sdfasd")
                listoffound=Bird_Trie.find_word(new_word[position:])

                if listoffound:
                    # print("True")
                    for found in listoffound:
                        global found_matches_B
                        found_matches_B += 1
                        if new_word[position:] == "barredowlet":
                            print("fasdf")
                        return bird_species.find_one(
                            {"concat_name": new_word[position:position+found]},
                            {"_id": 0, "common_name": 1})["common_name"]
    return False


# possibility search one worded bird names in one function and then multi worded bird names in another function.
# need to find where bird fam was initially found
# or can use trie to search for all 2+ worded birds

def find_bird_from_sentence(x):

    for fams in bird_fams:
        if re.search(rf"\W{fams}\W", x, flags=re.IGNORECASE):
            global found_matches_A
            copy_of_bird_specs = bird_specs
            new_list = list(filter(lambda a: fams in a['common_family'], copy_of_bird_specs))
            if len(new_list) == 1:
                # need to not search any longer
                print("this bird should be skipped", fams)

                found_matches_A += 1
                pass
            found = False
            for entries in new_list:
                if re.search(rf"(?:\W|^){entries['common_name']}", x, flags=re.IGNORECASE):
                    found_matches_A += 1
                    found = True
                    # print(x)
                    # print(entries)
                    return entries
                    break
            if not found:
                # print("not species\n",x)
                pass
            break
    return False


def get_bird_posts():
    bird_posts = list(my_col.find({}, {"_id": 0, "title": 1}))

    method_A = 0
    method_B = 0
    for x in bird_posts:
        print(x)
        tic = time.perf_counter()
        #print(find_bird_from_sentence(x["title"]))
        toc = time.perf_counter()
        method_A += toc - tic

        tic = time.perf_counter()
        print(new_find_bird_from_sentence(x["title"]))
        toc = time.perf_counter()
        method_B += toc - tic
        print("Method A\t", method_A, "Method B\t", method_B)

    print("Method A\t", method_A, "Method B\t", method_B)
    print(len(bird_posts), "posts")
    print(found_matches_A, "results A")
    print(found_matches_B, "results B")
    # current result is method B is faster and more accurate.
    # Method A	 69.55064550000003 Method B	 67.19713309999995
    # 1205 posts
    # 438 results A
    # 516 results B

    # print(re.findall(r"(?=(" + '|'.join(qwer) + r"))", x))

def testresults(x):
    print(new_find_bird_from_sentence(x))

if __name__ == '__main__':
    print('')
    # create_post_db()
    # create_species_db("birdlist.csv")
    #print(obtain_new_info())

    get_bird_families()
    make_trie()
    testresults("test with barred owlet")

    #print(len(bird_fams))
    get_bird_posts()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
