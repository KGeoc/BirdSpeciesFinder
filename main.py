import datetime as dt
import re
import praw
import pymongo
import credentials

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# TODO search get a list of all birds. Their scientific name if possible and english.

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

my_db = my_client["RedditInfo"]

my_col = my_db["RedditBirdPosts"]
my_col2 = my_db["RedditBirdSpecies"]


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
