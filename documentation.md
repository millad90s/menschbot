## Get News from API 
`https://api.mediastack.com/v1/news?access_key=bf69d3a450b6638e902a660ac20470df&languages=en&keywords=virus
`


## Todo 
* store news of each day into database to avoid run URL for every request , by the first request.
So if there is no record in database for today , then fetch the news from api. for simplisity just store the news in English language and foor health/food/sport category.