from flask_apscheduler import APScheduler
from export_events.export_events import main
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import logging
from logging.handlers import RotatingFileHandler
import os

# Set up logging for the scheduler
LOG_DIR = 'logs'
# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILENAME = 'logs/scheduler.log'
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3  # Keep 3 backup log files

# Create a rotating file handler
rotating_handler = RotatingFileHandler(LOG_FILENAME, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
rotating_handler.setFormatter(formatter)

# Set up the root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(rotating_handler)

def start_scheduler():
    scheduler = APScheduler()

    # # every hour at :00
    scheduler.add_job(id='export_events', func=main, trigger='cron', minute=0)
    
    # Add listeners for job execution and errors
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # Start the scheduler
    scheduler.start()

    # Keep the scheduler running in the background
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

# Scheduler setup and logging
def job_listener(event):
    """Listener function to log job execution events"""
    if event.exception:
        logging.error(f'Job {event.job_id} failed with exception: {event.exception}')
    else:
        logging.info(f'Job {event.job_id} completed successfully.')

if __name__ == '__main__':
    logging.debug('Scheduler წარმატებით გაეშვა')
    start_scheduler()