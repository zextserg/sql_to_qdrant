# Convert Query to proper SQL and to Qdrant filters
This script can convert text queries with combinations of AND/OR/NOT operators to SQL with proper WHERE clause and to relevant Qdrant filters.

## Part 1. Query to SQL
For example you have a standart SQL Database with table **posts** with key column **text** and data like:
- `green apples with yellow lemons`
- `mint and tomatos are the same`
- `oranges with apples are like lemons`

And you want to search substrings by just simple query: `apples AND oranges AND NOT tomatos`  
Or you want to make complex query, but don't want to trace all `like '%...%'` parts, you just want to search by query:  
`(apples AND oranges) OR (tomatos AND (lemons OR mint))`

So, this script help you to convert such queries to SQL query with proper WHERE Clause.
With using func **convert_init_query_to_proper_sql_where_clause(init_query, key)** you can convert for example:  
`apples AND oranges AND NOT tomatos`  
to  
`SELECT * FROM posts WHERE ( text ILIKE '%apples%' AND text ILIKE '%oranges%' AND text NOT ILIKE '%tomatos%')`   

\* - func argument **key** -  it's a name of your text column in SQL DB

## Part 2. SQL to Qdrant Filters
Then, if you have your data in [Qdrant](https://github.com/qdrant) Database and also want to search by exact match as substring of some text field, my script can convert your query to proper Qdrant Filters.  
For that case you can use func **convert_sql_where_to_qdrant_filters(sql_where_clause, res_type='json', make_lowercase=False)** which return 2 types of result: as `json` or as `Python Qdrant Filter models`  

For example you can convert:  
`potato OR (oranges AND mint)`  
to **JSON** Qdrant Filters  
```
{
    "should": [
        {
            "key": "text",
            "not": false,
            "match": {
                "text": "potato"
            }
        },
        {
            "must": [
                {
                    "key": "text",
                    "not": false,
                    "match": {
                        "text": "oranges"
                    }
                },
                {
                    "key": "text",
                    "not": false,
                    "match": {
                        "text": "mint"
                    }
                }
            ]
        }
    ]
}
```
or to **Python Qdrant Filter Models**  
```
Filter(should=[
  FieldCondition(key='text', match=MatchText(text='potato'), ...),
  Filter(must=[
    FieldCondition(key='text', match=MatchText(text='oranges'), ...),
    FieldCondition(key='text', match=MatchText(text='mint'), ...)
  ], ...)
], ...)
```

If you have installed and run qdrant locally (you can run it with docker: `docker run -p 6333:6333 qdrant/qdrant:latest`)  
this script will connect to it, create simple collection with test data and then it convert a list of test qeuries first to SQL queries and next - to Qdrant Filters (both - JSON and Models).  
And then script will search each query in Qdrant Database and show all founded results for each query.  
Here is a list of test queries and which results (answers) should be found in test data:  
- `'apples AND oranges', # answer ids: 3,6`
- `'tomatos OR mint', # answer ids: 2,4,5,6`
- `'apples AND oranges AND NOT tomatos', # answer ids: 3`
- `'potato OR (oranges AND mint)', # answer ids: 4,6`
- `'apples AND (NOT tomatos OR lemons) AND (oranges AND NOT mint)',  # answer ids: 3`
- `'(apples AND oranges) OR (tomatos AND (lemons OR mint))', # answer ids: 2,3,6`
- `'oranges AND (NOT lemons OR potato) AND (mint AND NOT (apples OR tomatos))', # answer ids: 4`
- `'apples AND NOT all AND (lemons OR potato OR (oranges AND NOT (tomatos OR mint)))' # answer ids: 1,3`  

\* - if you sure have all data in Qdrant text field in lowercase or you create [Qdrant full-text index](https://qdrant.tech/articles/qdrant-introduces-full-text-filters-and-indexes/#full-text-search-behaviour-on-an-indexed-payload-field) with lowercase param  
you can set func argument **make_lowercase** to True and all data inside Filetrs values will be lowercased in results
