import csv
import re
import pymongo

my_client = pymongo.MongoClient("mongodb://localhost:27017/")

my_db = my_client["BirdInfo"]
bird_species = my_db["BirdSpecies"]


# files should be a .csv in withe the following setup
# Common Name,Family,Scientific name
# where scientific name includes genus and species
def file_import(file_name):
    # makes common_name be the unique index.
    bird_species.create_index("common_name", unique=True)
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        # use next to get rid of header row
        next(reader)

        for row in reader:
            if bird_species.find_one({'common_name': row[0]}):
                continue
            else:
                holder = row[2].split()
                bird_species.insert_one(
                    {"common_name": row[0],
                     "common_family": row[0].split()[-1],
                     "family_name": row[1],
                     "genus": holder[0],
                     "species": holder[1],
                     "concat_name": re.sub('[^a-zA-Z0-9]', '', row[0]).lower()
                     })
