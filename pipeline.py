import os
import time
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
from dotenv import load_dotenv

load_dotenv()

class Pipeline:
    def __init__(self, config_path):
        """Initialize the pipeline with configuration and Redis connection"""
        self.config_path = config_path
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        # Redis connection with timeout
        self.redis_conn = Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0,
            socket_connect_timeout=5
        )
        
        # Initialize queue and scheduler
        self.task_queue = Queue('default', connection=self.redis_conn)
        self.scheduler = Scheduler(connection=self.redis_conn, queue=self.task_queue)
        
        # Setup output directory
        self.output_base = Path(self.config['output_base'])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = self.output_base / f"dataset_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def schedule_extractions(self):
        """Schedule Reddit and Roboflow jobs with proper intervals"""
        from tasks import run_reddit_job, run_roboflow_job
        
        # Clear existing schedules
        for job in self.scheduler.get_jobs():
            self.scheduler.cancel(job)
        
        # Convert hours to seconds for RQ Scheduler
        reddit_interval = self.config['scheduling']['reddit_interval_hours'] * 3600
        roboflow_interval = self.config['scheduling']['roboflow_interval_hours'] * 3600
        
        # Schedule Reddit job (in seconds)
        self.scheduler.schedule(
            scheduled_time=datetime.utcnow(),
            func=run_reddit_job,
            args=(self.config_path,),
            interval=reddit_interval,
            queue_name='default',
            meta={'description': 'Reddit image download'}
        )
        
        # Schedule Roboflow job (in seconds)
        self.scheduler.schedule(
            scheduled_time=datetime.utcnow() + timedelta(minutes=5),
            func=run_roboflow_job,
            args=(self.config_path,),
            interval=roboflow_interval,  # Now passing integer seconds
            queue_name='default',
            meta={'description': 'Roboflow dataset download'}
        )

    def run_workers(self, num_workers=4):
        """Start worker processes"""
        from multiprocessing import Process
        from worker import start_worker
        
        workers = []
        for i in range(num_workers):
            p = Process(target=start_worker)
            p.start()
            workers.append(p)
            print(f"Started worker {i+1} (PID: {p.pid})")
        
        return workers

    def monitor_queue(self):
        """Monitor queue status"""
        try:
            while True:
                print(f"\nQueue status at {datetime.now()}")
                print(f"Pending jobs: {len(self.task_queue)}")
                print(f"Failed jobs: {len(self.task_queue.failed_job_registry)}")
                time.sleep(10)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")

if __name__ == "__main__":
    pipeline = Pipeline("config.yaml")
    pipeline.schedule_extractions()
    workers = pipeline.run_workers()
    
    try:
        pipeline.monitor_queue()
    finally:
        for w in workers:
            w.terminate()