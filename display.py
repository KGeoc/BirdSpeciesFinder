import retrieval


if __name__ == '__main__':
    families=retrieval.count_all_found_species(gt=20)

    for x in families:
        print("{} [{}] {}".format("bird",x["count"],x["_id"]))

