import os
import logging
import datetime
import shutil
import time
import schedule

# Set up logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "application.log")
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def main_task():
    """
    This is the main recurring task that will be executed on schedule.
    Replace the contents of this function with your actual code.
    """
    logging.info("Main task started")
    # TODO: Add your main task code here
    # For example:
    # process_data()
    # update_database()
    # send_notifications()
    logging.info("Main task completed")

def cleanup():
    """
    This function performs cleanup operations to manage disk space and remove unnecessary files.
    """
    logging.info("Starting cleanup")
    
    # Clean up old log files
    current_time = datetime.datetime.now()
    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        if current_time - file_modified > datetime.timedelta(days=7):
            os.remove(file_path)
            logging.info(f"Removed old log file: {filename}")
    
    # Clean up any temporary files or directories your main task might create
    temp_dir = "temp"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        logging.info("Removed temporary directory")
    
    # TODO: Add any other cleanup tasks here
    # For example:
    # delete_old_backups()
    # clear_cache()
    
    logging.info("Cleanup completed")

def run_scheduled_task():
    """
    This function wraps the main task and cleanup operations.
    It's designed to be called by the scheduler.
    """
    try:
        main_task()
    finally:
        cleanup()

# Schedule the task to run every hour
schedule.every().hour.do(run_scheduled_task)

if __name__ == "__main__":
    logging.info("Script started")
    
    # Run the scheduled task immediately once
    run_scheduled_task()
    
    # Then enter the scheduling loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Wait for 60 seconds before checking the schedule again