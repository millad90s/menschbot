### tagesschau api
from datetime import datetime
import dataclasses
import logging
import random
import requests
import json
import os


from chatgpt_module import get_de_words_definition
from .news import News

### read basic env from .env file 
from dotenv import load_dotenv
load_dotenv()

NEWS_URL = os.getenv("NEWS_URL")
regions = [ "Baden-Württemberg", "Berlin", "Hamburg"]
ressort = [ "wirtschaft" ]


# ## curl -X 'GET' \
#   'https://www.tagesschau.de/api2u/news/ \
#   -H 'accept: application/json'
def read_news( NEWS_URL: str= "https://www.tagesschau.de/api2u/news/?", regions: str = "3", ressort: str = 'wirtschaft', count: int = 2) -> list[News]:
    try:
        today_date = datetime.now().strftime('%Y-%m-%d')
        if not os.path.exists("german-news"+today_date+".json"):
            response = requests.get(NEWS_URL + f"regions={regions}&ressort={ressort}")
            logging.info(f"News fetched: {response.status_code}")
            data = response.json()['news']
            news = random.sample(data, count)
            German_news = []
            for new in news:
                title = new['title']
                description = new['firstSentence']
                date = new['date']
                shareURL = new['shareURL']
                teaserImage = new['teaserImage']['imageVariants']['16x9-512']
                videoURL=""
                ### check if video key exists in json 
                if 'video' in new:
                    videoURL = new['video']['stream']['h264s']
                    
                    # Load the existing JSON data from the file
                    with open('german_podcast.json', 'r') as f:
                        video_urls = json.load(f)

                    # Append the new URL to the list
                    new_url = videoURL
                    video_urls.append({"videoURL": new_url})

                    # Write the updated JSON data back to the file
                    with open('german_podcast.json', 'w') as f:
                        json.dump(video_urls, f, indent=4)

                learning_text = get_de_words_definition(description)
                myNews = News(title=title, url = shareURL, urlToImage= teaserImage, date = date,
                              description = description, learning_text = learning_text, videoURL=videoURL)
                German_news.append(myNews)
                
            logging.info(f"length of news: {len(German_news)}")
            return German_news
        else:
            with open("german-news"+today_date+".json", "r") as file:
                logging.info(f"news_{today_date}.json file found")
                news_data = json.load(file)
                return news_data
    except Exception as e:
        print(f"Error fetching news: {e}")
        
        
### fetch videow news
def fetch_videos_news():
    try:
        NEWS_URL = 'https://www.tagesschau.de/api2u/news/?regions=3&ressort=video' 
        response = requests.get(NEWS_URL)
        logging.info(f"News fetched: {response.status_code}")
        rando = random.sample(response.json()['news'],1)
        title = rando[0]['title']
        data = rando[0]['streams']['h264s']
        logging.info(f"URL of video news: {data}")
        return (title,data)
    except Exception as e:
        print(f"Error fetching news: {e}")
        
### if file german-news.json does not existsfor today then write/create it and write the news into it
def write_news(news):
    try:
        date = datetime.now().strftime('%Y-%m-%d')
        logging.info(f"news_{date}.json file created")
        if not os.path.exists("german-news"+date+".json"):
            ### if file german-news.json does not exists for today then create it 
            news_dict = []
            for item in news:
                news_dict.append(item.__dict__)
                
            with open("german-news"+date+".json", "w") as file:
               file.write(json.dumps(news_dict))
            return True
    except Exception as e:
        print(f"Error writing news: {e}")
        
rn = read_news(count=24)
write_news(rn)
