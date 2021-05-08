import csv

import pymongo

my_client = pymongo.MongoClient("mongodb://localhost:27017/")

my_db = my_client["BirdInfo"]
bird_species = my_db["BirdSpecies"]

#files should be a .csv in withe the following setup
#Common Name,Family,Scientific name
#where scientific name includes genus and species
def file_import(file_name):
    #makes common_name be the unique index.
    bird_species.create_index({"common_name": 1}, {"unique": True})
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        #use next to get rid of header row
        next(reader)

        for row in reader:
            holder=row[2].split()
            print(row[0], row[0].split()[-1], row[1], holder[0], holder[1], sep='\t')
            bird_species.insert_one({'common_name': row[0],
                                     "common_family": row[0].split()[-1],
                                     "family_name": row[1],
                                     "genus": row[2].split()[0],
                                     "species": row[2].split()[1]
                                     })

