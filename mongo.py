#!/usr/bin/env python3

from housepy import config, log
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId

mongo = config['mongo']
client = MongoClient(mongo['host'], mongo['port'])
db = client[mongo['database']]

def rebuild_indexes():

    try:
        index_names =  [index['name'] for index in list(db.entries.list_indexes())]
        for index_name in index_names:
            if index_name == "_id_":
                continue
            db.entries.drop_index(index_name)    
    except Exception as e:
        log.error(log.exc(e))
        return

    try:
        db.entries.create_index("site")
        db.entries.create_index([("t_utc", ASCENDING)])
        db.entries.create_index([("site", ASCENDING), ("t_utc", ASCENDING)], unique=True)        
    except Exception as e:
        log.error(log.exc(e))
        return

if __name__ == "__main__":
    rebuild_indexes()


