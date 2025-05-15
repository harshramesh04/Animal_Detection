from redis import Redis
from rq.queue import Queue

def test_redis():
    try:
        conn = Redis(host='localhost', port=6379)
        conn.ping()
        print("Redis connection successful")
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False

def test_rq():
    try:
        from rq import Queue
        q = Queue(connection=Redis())
        print("RQ queue initialization successful")
        return True
    except Exception as e:
        print(f"RQ setup failed: {e}")
        return False

if __name__ == "__main__":
    test_redis()
    test_rq()