import praw
import os
import requests
import time
import random
from typing import List, Dict

class RedditImageDownloader:
    def __init__(self, credentials: Dict):
        self.reddit = praw.Reddit(
            user_agent=True,
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            username=credentials["username"],
            password=credentials["password"]
        )
    
    @staticmethod
    def is_image_url(url: str) -> bool:
        return url.endswith((".jpg", ".jpeg", ".png"))
    
    def download_image(self, url: str, path: str) -> bool:
        try:
            img_data = requests.get(url, timeout=10).content
            with open(path, "wb") as f:
                f.write(img_data)
            print(f"Downloaded: {url}")
            return True
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return False
    
    def scrape_subreddit(
        self,
        subreddit_name: str,
        keywords: List[str],
        output_dir: str,
        limit_per_subreddit: int = 1000
    ) -> None:
        print(f"\nScraping subreddit: {subreddit_name}")
        subreddit = self.reddit.subreddit(subreddit_name)
        
        posts = list(subreddit.top(limit=limit_per_subreddit)) + \
                list(subreddit.new(limit=limit_per_subreddit)) + \
                list(subreddit.hot(limit=limit_per_subreddit))
        
        print(f"Total posts fetched: {len(posts)}")
        
        for submission in posts:
            if any(keyword in submission.title.lower() for keyword in keywords) and self.is_image_url(submission.url):
                image_url = submission.url
                image_name = f"{submission.id}.jpg"
                image_path = os.path.join(output_dir, image_name)
                
                if not os.path.exists(image_path):
                    if self.download_image(image_url, image_path):
                        time.sleep(random.uniform(1, 3))

def main():
    # Configuration (Move to config.yaml later)
    credentials = {
        "client_id": "nnU4497d0saUdjXMTxAQcg",
        "client_secret": "qdForicKYGjwC0jkIlq0rzUK8BAkLg",
        "username": "Victorfrank_04",
        "password": "Victorfrank@04"
    }
    
    # Define your classes and related subreddits
    CLASS_CONFIG = {
        "squirrel": {
            "subreddits": ["squirrels", "aww", "nature", "AnimalsBeingBros"],
            "keywords": ["squirrel"]
        },
        "snake": {
            "subreddits": ["snakes", "reptiles", "nature", "AnimalsBeingDerps"],
            "keywords": ["snake", "cobra", "python", "viper"]
        },
        "raccoon": {
            "subreddits": ["raccoons", "aww", "AnimalsBeingBros"],
            "keywords": ["raccoon", "trash panda"]
        }
    }
    
    downloader = RedditImageDownloader(credentials)
    
    for class_name, config in CLASS_CONFIG.items():
        output_dir = f"{class_name}_images"
        os.makedirs(output_dir, exist_ok=True)
        
        for subreddit in config["subreddits"]:
            downloader.scrape_subreddit(
                subreddit_name=subreddit,
                keywords=config["keywords"],
                output_dir=output_dir
            )

if __name__ == "__main__":
    main()