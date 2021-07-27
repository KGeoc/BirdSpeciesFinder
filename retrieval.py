import re
import pymongo


my_client = pymongo.MongoClient("mongodb://localhost:27017/")

my_db = my_client["BirdInfo"]

my_col = my_db["RedditBirdPosts"]
bird_species = my_db["BirdSpecies"]


def obtain_nonvalid_posts():
    return list(my_col.find({"species": None}, {"_id": 0, "title": 1, "post_id": 1})
                .sort('date', pymongo.DESCENDING))


def count_all_found_families(gt=0):
    return list(
        my_col.aggregate([
            {"$group":
                 {"_id": "$family_name",
                  "count": {"$sum": 1}
                  }
             },
            {"$sort":
                 {'count': -1}
             },
            {"$match":
                {
                    'count': {'$gt': gt},
                    '_id': {'$ne': None}
                }
            }
        ])
    )


def count_all_found_species(gt=0):
    return list(
        my_col.aggregate([
            {"$group":
                 {"_id": "$species",
                  "count": {"$sum": 1}
                  }
             },
            {"$sort":
                 {'count': -1}
             },
            {"$match":
                {
                    'count': {'$gt': gt},
                    '_id': {'$ne': None}
                }
            }
        ])
    )


def display_found_families(gt=0):
    for post in count_all_found_families(gt):
        print(post)


def display_found_species(gt=0):
    for post in count_all_found_species(gt):
        print(post)


def find_family(family):
    return my_col.find({"family_name": re.compile(family, re.IGNORECASE)})


def display_by_family(family):
    for x in find_species(family):
        print(x)


def find_species(species):
    return my_col.find({"species": re.compile(species, re.IGNORECASE)})


def display_by_species(species):
    for x in find_species(species):
        print(x)


if __name__ == '__main__':
    print('')
    # for post in obtain_nonvalid_posts():
    #    print(post)
    display_found_species()
    # display_by_species("purpl")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
