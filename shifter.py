import os
import shutil
import re
import datetime
import sys
from pathlib import Path
import json
import platform
import shutil
import time
import schedule


# Set up global log-related variables
LOG_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logs")
LOG_FILE_PREFIX = "log_"
DEBUG_LOG_FILE_PREFIX = "debug_"
LOG_FILE_EXTENSION = ".log"
LOG_FILE_NAME_FORMAT = "{}" + LOG_FILE_EXTENSION
LOG_DEBUG_PATH = os.path.join(LOG_FOLDER, DEBUG_LOG_FILE_PREFIX +
LOG_FILE_NAME_FORMAT.format(datetime.datetime.today().strftime("%Y-%m-%d")))
LOG_PATH = os.path.join(LOG_FOLDER, LOG_FILE_PREFIX +
LOG_FILE_NAME_FORMAT.format(datetime.datetime.today().strftime("%Y-%m-%d")))



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
            f.write(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}\n")


def write_to_debug_log(log_path, messages):
    """Writed log messages to debug file"""
    # print(write_to_debug_log.__doc__)
    with open(log_path, "a") as f:
        for message in messages:
            f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}\n")


def copy_files_job():
    """Function to copy files"""
    copy_files_in_folders()
    write_to_debug_log(LOG_DEBUG_PATH, ["Copy job is running"])


def run_copy_job():
    """Scheduled the copy job to run at a specific time"""
    config = read_config()
    scheduled_every_15_minutes = config.get("scheduled_every_15_minutes")
    scheduled_every_hour = config.get("scheduled_every_hour")
    scheduled_time_str = config.get("scheduled_on_time")
    print(scheduled_every_15_minutes)
    print(scheduled_every_hour)
    print(scheduled_time_str)
    if scheduled_every_15_minutes:
        schedule.every(15).minutes.at(':00').do(copy_files_job)
        write_to_debug_log(LOG_DEBUG_PATH, [f"Copy job scheduled to run 15 minutes"])

    if scheduled_time_str:
        try:
            hour, minute = [int(x) for x in scheduled_time_str.split(":")]
            if hour >= 0 and hour < 24 and minute >= 0 and minute < 60:
                # Schedule job to run at the specified time
                schedule.every().day.at(scheduled_time_str).do(copy_files_job)
                write_to_debug_log(LOG_DEBUG_PATH, [f"Copy job scheduled to run at {scheduled_time_str}"])
            else:
                print("Invalid scheduled time format in config file. Using default schedule.")
        except ValueError:
            print("Invalid scheduled time format in config file. Using default schedule.")
    
    if scheduled_every_hour:
        # Use default schedule if no scheduled time is specified in config file
        schedule.every(1).hour.at(':00').do(copy_files_job)
        write_to_debug_log(LOG_DEBUG_PATH, [f"Copy job scheduled to run every hour"])

    while True:
        pending_jobs = schedule.jobs
        print(f"{len(pending_jobs)} jobs pending. Waiting...")
        schedule.run_pending()
        time.sleep(1)
        

def check_and_create_folder(folder_path, log_messages):
    """Checked if folder exists, create it if it doesn't"""
    # print(check_and_create_folder.__doc__)
    print("folder_path", folder_path)

    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            log_messages.append(f"Created folder '{folder_path}'")
        except Exception as e:
            log_messages.append(f"Error creating folder '{folder_path}': {e}")


def get_files(source_dir, ext, pattern=None):

    files = []
    print("source_dir: ", source_dir)
    print("ext: ", ext)
    print("pattern: ", pattern)
    for file in os.listdir(source_dir):
        if any(file.endswith(e) for e in ext) and (not pattern or re.search(pattern, file)):
            files.append(os.path.join(source_dir, file))
    return files


def copy_files_in_folders():
    """Copies files from source folders to destination folders"""
    config = read_config()
    dest_folders = config["destination_folders"]
    log_messages = []
    total_count = 0

    # Get source folders from config
    source_folders = [os.path.expandvars(folder) for folder in config["source_folders"]]

    print("dest_folders: ",dest_folders)
    print("source_folders: ",source_folders)

    for source_folder in source_folders:
        if not os.path.exists(source_folder):
            log_messages.append(f"Source folder '{source_folder}' does not exist")
            continue

        print("source_folder: ", source_folder)

        for folder_name, folder_config in dest_folders.items():
            dest_dir = folder_config["path"]
            check_and_create_folder(dest_dir, log_messages)

            ext = folder_config["file_extensions"]
            delete_after_copy = folder_config["delete_after_copy"]
            pattern = folder_config.get("pattern")

            files_to_copy = get_files(source_folder, ext, pattern)
            if not files_to_copy:
                log_messages.append(f"No files found to copy in '{source_folder}'")
                continue

            # Get a list of files in the destination folder
            dest_files = set(os.listdir(dest_dir))
            print("dest_files: ",dest_files)

            # Copy files that haven't been copied already
            count = 0
            for file_path in files_to_copy:
                file_name = os.path.basename(file_path)

                if file_name in dest_files:
                    # If the file already exists in the destination folder, skip it
                    continue

                # Copy the file to the destination folder
                dest_path = os.path.join(dest_dir, file_name)
                shutil.copy2(file_path, dest_path)
                count += 1
                print("file_name: ",file_name)
                print("file_path: ",file_path)
                # Add the name of the copied file to the set of destination files
                dest_files.add(file_name)
                # If delete_after_copy is True, delete the original file
                if delete_after_copy:
                    try:
                        os.remove(file_path)
                        write_to_debug_log(LOG_DEBUG_PATH, [f"Deleted {file_name} from {source_folder}\n"])
                    except OSError as e:
                        log_messages.append(f"Error deleting {file_name} from {source_folder}: {e}")
                        
            total_count += count
            log_messages.append(f"Copied {count} files from {source_folder} to {dest_dir}")

            # Write filenames to debug log
            write_to_debug_log(LOG_DEBUG_PATH, [f"Copied {file_name} from {source_folder} to {dest_dir}\n"])


    # write all log messages to file
    write_to_log(LOG_PATH, log_messages)
    write_to_debug_log(LOG_DEBUG_PATH, log_messages)

    # write total count to log
    print(f"Total files copied: {total_count}")
    write_to_log(LOG_PATH, [f"Total files copied: {total_count}"])
    write_to_debug_log(LOG_DEBUG_PATH, [f"Total files copied: {total_count}"])


if __name__ == '__main__':
    script_path = Path(sys.argv[0]).resolve()
    os.chdir(script_path.parent)
    while True:
        try:
            print("Started...")
            logs_dir = Path.cwd() / "Logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            write_to_log(LOG_PATH, [f"Service started..."])
            write_to_debug_log(LOG_DEBUG_PATH, [f"Service started..."])
            copy_files_in_folders()
            run_copy_job()

        except:
            print("Stopping...")
            sys.exit()