import json
import os
import platform
import shutil
import re
import datetime
import signal
import time
import schedule


# Set up global log-related variables
LOG_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logs")
LOG_FILE_PREFIX = "log_"
DEBUG_LOG_FILE_PREFIX = "debug_"
LOG_FILE_EXTENSION = ".log"
LOG_FILE_NAME_FORMAT = "{}_{}" + LOG_FILE_EXTENSION
LOG_DEBUG_PATH = os.path.join(LOG_FOLDER, DEBUG_LOG_FILE_PREFIX + LOG_FILE_NAME_FORMAT.format(datetime.datetime.today().strftime("%Y-%m-%d"), "debug"))
LOG_PATH = os.path.join(LOG_FOLDER, LOG_FILE_PREFIX + LOG_FILE_NAME_FORMAT.format(datetime.datetime.today().strftime("%Y-%m-%d"), "regular"))


def read_config():
    with open("config.json", "r") as f:
        config = json.load(f)

    # Modify destination folder paths for different operating systems
    if platform.system() == "Windows":
        for folder_name, folder_config in config["destination_folders"].items():
            folder_config["path"] = os.path.join("C:", folder_config["path"])
    else:
        for folder_name, folder_config in config["destination_folders"].items():
            folder_config["path"] = os.path.join("/", folder_config["path"])

    return config


def write_to_log(log_path, messages):
    """Writed log messages to file"""
    # print(write_to_log.__doc__)
    with open(log_path, "a") as f:
        for message in messages:
            f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}\n")


def write_to_debug_log(log_path, messages):
    """Writed log messages to debug file"""
    # print(write_to_debug_log.__doc__)
    with open(log_path, "a") as f:
        for message in messages:
            f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}\n")


def run_copy_job():
    """Scheduled the copy job to run at a specific time"""
    # print(run_copy_job.__doc__)
    config = read_config()
    scheduled_time_str = config.get("scheduled_on_time")
    if scheduled_time_str:
        try:
            hour, minute = [int(x) for x in scheduled_time_str.split(":")]
            if hour >= 0 and hour < 24 and minute >= 0 and minute < 60:
                # Schedule job to run at the specified time
                schedule.every().day.at(scheduled_time_str).do(run_copy_job)
            else:
                print("Invalid scheduled time format in config file. Using default schedule.")
        except ValueError:
            print("Invalid scheduled time format in config file. Using default schedule.")
    else:
        # Use default schedule if no scheduled time is specified in config file
        schedule.every(1).hour.do(run_copy_job)

    while True:
        schedule.run_pending()
        time.sleep(1)

# define a signal handler to catch the interrupt signal
def signal_handler(signal, frame):
    print("Stopping...")
    # perform any necessary cleanup here
    # ...
    exit(0)

# set the signal handler
signal.signal(signal.SIGINT, signal_handler)