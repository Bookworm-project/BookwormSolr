## Query Parsing
This will be handled by the SOLR side, which already has infrastructure to convert JSON queries into the Lucene Query language. 

Adapting the translation of Bookworm API to Solr will need to be done later, but here's what needs to be done.

## What's missing from Lucene

- GREP searches (see wildcards)
- Case-sensitivity. This requires a difference indexer (I think..) and query parser than the default

## Lucene features missing from Bookworm API

- Wildcard searches: te?t, te*t  (single character wildcard, multiple character wildcard)
- Fuzzy searches, based on levenshtein distance or edit distance. 
  - e.g. worm~ also match worn. Degree of similarity can be specified: e.g. worn~0.8
- Proximity search
  - hathitrust center"~5
  - range queries for text. e.g. title:{apple TO zebra}
  - term boosting. e.g. Hathitrust^10 Research Center

## Outstanding questions

- name of regular expressions in BW API: grep or re
- support for backend-specific features
- UI integration of warnings with missing features
- which lucene features /should/ we support?
- see also [Open Questions in Bookworm docs](http://bookworm-project.github.io/Docs/Search_Limiting.html)

## Comparison

#### Bookworm

```
"search_limits":{
    "author_gender":["Female"],
    "country":["United States","Germany","East Germany","West Germany"],
    "publish_year":[1890]
    }
```

#### Lucene

```+author_gender:female +(country:"united states" country:germany country:"east germany" country:"west germany") +publish_year:1890```

### Exclusion

#### Bookworm

````
{"country":{"$ne":["United States","Canada"]}}
````

#### Lucene

```
country:(-"United States" -"Canada") 
```
### Range Queries
Ranges are inclusive in Lucene, so 
```
{"publish_year":{"$lte":1950,"$gte":1900}
```
and
```
{"publish_year":{"$lte":1950,"$gt":1899}
```
need to be represented as
```
	+publish_year:[1950 TO 1899]
```
in Lucene.

# And/Or

## Bookworm

```
{"$or":[
      {"country":["USA"]},
      {"author_birth_country":["USA"]}
]}
```
In Lucene, OR is implicit, but can be explicated 
```
(country:USA author_birth_country:USA) 
```
or,
``` 
+(country:USA OR author_birth_country:USA)
```

### Complex Queries

```
"search_limits":{
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
}
```

### Lucene

```
(+(year:[1980 TO 1992] year:[2001 TO 2008]) +author_party:Republican) OR (+(year:[1993 TO 2000] year:2009) +author_party:Democrat)
```

