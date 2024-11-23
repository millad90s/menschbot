### define an standard class for news object and all the apis should return data in this format

from dataclasses import asdict, dataclass
from typing import List


@dataclass
class News:
    def __init__(self, title: str, description: str = None, url: str = None,
                 urlToImage: str = None, source: str = None, learning_text: str = None, 
                 date: str = None, videoURL: str = None):
        self.title = title
        self.description = description
        self.url = url
        self.urlToImage = urlToImage
        self.source = source
        self.learning_text = learning_text
        self.date = date
        self.videoURL = videoURL
    
    def __str__(self) -> str:
        return self.title

def list_to_dict( news_list: List[News]) -> List[dict]:
    return [asdict(news) for news in news_list]