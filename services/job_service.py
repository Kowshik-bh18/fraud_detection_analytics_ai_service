import threading
import uuid

job_store = {}


def create_job():
    job_id = str(uuid.uuid4())
    job_store[job_id] = {"status": "processing"}
    return job_id


def update_job(job_id, data):
    job_store[job_id] = data


def get_job(job_id):
    return job_store.get(job_id)


def run_async(target, args=()):
    thread = threading.Thread(target=target, args=args)
    thread.start()