import logging
import request_parser as rp

def main():
    logging.basicConfig(level=logging.DEBUG)

    test_queries = [
    '''{"search_limits":{
    "author_gender":["Female"],
    "country":["United States","Germany","East Germany","West Germany"],
    "publish_year":[1890]
    }}''',
    '''{"search_limits":{
    "author_gender":{"$eq":"Female"},
    "country":{
        "$eq":["United States","Germany","East Germany","West Germany"],
        "$ne":["United States","Germany","East Germany","West Germany"]
        },
    "publish_year":{"$lte":1950,"$gte":1900}
    }}''',
    '''{"search_limits":{
    "$or":[
        {
            "year":{
                "$or":[
                    {"$gte":1980,"$lte":1992},
                    {"$gte":2001,"$lte":2008}
                    ]
                },
            "author_party":"Republican"
        },
        {
            "year":{
                "$or":[
                    {"$gte":1993,"$lte":2000},
                    {"$gte":2009}
                    ]
            },
            "author_party":"Democrat"
        }
    ]
    }}'''
            ]


    parser = rp.RequestParser("http://localhost:8983/solr/collection1/")

    for q in test_queries:
        logging.debug("Testing Bookworm Query: {0}".format(q))
        url = parser.query(q)
        logging.info("Solr output {0}".format(url))



if __name__ == '__main__':
    main()
