_:
    @just -l -u

run example:
    #!/usr/bin/env bash
    [ -f ./compose/dc-{{example}}.yml ] && docker-compose -f ./compose/dc-{{example}}.yml up -d 
    [ -f ./data/data-{{example}}.json ] && just load ./data/data-{{example}}.json 
    uvicorn example-{{example}}:app --reload
    [ -f ./compose/dc-{{example}}.yml ] &&  docker-compose -f ./compose/dc-{{example}}.yml down

load datafile:
    #!/usr/bin/env python3
    from pymongo import MongoClient, InsertOne
    from bson.objectid import ObjectId
    import json
    db = MongoClient().db
    with open('{{datafile}}') as f:
        data = json.loads(f.read())
        for k, items in data.items():
            bulk = []
            for v in items:
                current = v
                current['id'] = str(ObjectId())
                current['checked_out'] = False
                bulk.append(InsertOne(current))
            db[k].bulk_write(bulk)
