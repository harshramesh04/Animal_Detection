import yaml
from pathlib import Path
from roboflow_downloader import RoboflowDownloader
from reddit_downloader import RedditImageDownloader
import time

def run_reddit_job(config_path):
    """Task function for Reddit downloads"""
    print(f"Starting Reddit download job with config: {config_path}")
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        downloader = RedditImageDownloader(config['reddit_credentials'])
        output_dir = Path(config['output_base']) / "reddit_images"
        output_dir.mkdir(exist_ok=True)
        
        for class_name, class_config in config['reddit_classes'].items():
            class_dir = output_dir / class_name
            class_dir.mkdir(exist_ok=True)
            
            for subreddit in class_config['subreddits']:
                downloader.scrape_subreddit(
                    subreddit_name=subreddit,
                    keywords=class_config['keywords'],
                    output_dir=str(class_dir),
                    limit_per_subreddit=config['download_limits']['reddit']
                )
                time.sleep(config['rate_limits']['reddit'])
                
    except Exception as e:
        print(f"Reddit job failed: {e}")
        raise

def run_roboflow_job(config_path):
    """Task function for Roboflow downloads"""
    print(f"Starting Roboflow download job with config: {config_path}")
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        downloader = RoboflowDownloader(config['roboflow_api_key'])
        output_dir = Path(config['output_base']) / "roboflow_images"
        output_dir.mkdir(exist_ok=True)
        
        for class_name, class_config in config['roboflow_classes'].items():
            downloader.download_dataset(
                workspace=class_config['workspace'],
                project=class_config['project'],
                version=class_config['version'],
                class_name=class_name,
                output_dir=str(output_dir / class_name)
            )
            time.sleep(config['rate_limits']['roboflow'])
            
    except Exception as e:
        print(f"Roboflow job failed: {e}")
        raise