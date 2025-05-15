from redis import Redis
from rq.worker import Worker
from rq.queue import Queue
from rq.registry import StartedJobRegistry
import logging
import socket
import os
import time

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('worker.log'),
        logging.StreamHandler()
    ]
)

def start_worker():
    """Start an RQ worker with unique naming and cleanup"""
    try:
        # Initialize Redis connection
        redis_conn = Redis(
            host='localhost',
            port=6379,
            db=0,
            socket_connect_timeout=5
        )
        
        # Clean up any stale workers
        StartedJobRegistry('default', connection=redis_conn).cleanup()
        
        # Create unique worker name
        worker_name = f"worker_{socket.gethostname()}_{os.getpid()}_{int(time.time())}"
        
        # Initialize worker
        worker = Worker(
            queues=['default'],
            connection=redis_conn,
            name=worker_name,
            default_worker_ttl=600,  # Auto-cleanup if worker crashes
            job_monitoring_interval=5  # Check for new jobs every 5 seconds
        )
        
        logging.info(f"🚀 Starting worker {worker_name}")
        logging.info(f"🔗 Connected to Redis at localhost:6379")
        logging.info(f"👂 Listening on queue: default")
        
        # Start working (burst=False for continuous operation)
        worker.work(with_scheduler=True)
        
    except Exception as e:
        logging.error(f"❌ Worker failed: {str(e)}")
        raise

if __name__ == "__main__":
    start_worker()