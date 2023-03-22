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
"""
read_config: a function that reads a JSON file containing the configuration for the script, and returns a dictionary containing the configuration. The function modifies the paths of the destination folders depending on the operating system.
check_and_create_folder(folder_path, log_messages): a function that checks if a folder exists, and creates it if it doesn't. It takes two arguments: folder_path, which is the path of the folder to check/create, and log_messages, which is a list of log messages that will be updated depending on whether the folder was created or not.
write_to_log(log_path, messages): a function that writes log messages to a log file. It takes two arguments: log_path, which is the path of the log file to write to, and messages, which is a list of log messages to write.
write_to_debug_log(log_path, messages): a function that writes debug log messages to a debug log file. It takes two arguments: log_path, which is the path of the debug log file to write to, and messages, which is a list of debug log messages to write.
get_files(source_dir, ext, pattern=None): a function that returns a list of file paths in the source directory with the given extension and pattern. It takes three arguments: source_dir, which is the path of the source directory, ext, which is a list of file extensions to filter by, and pattern, which is a regular expression pattern to match file names against.
copy_then_remove_files(source_folder, dest_folder, ext, delete_after_copy=False, pattern=None): a function that copies files with specified extensions and pattern from source directory to destination directory and optionally deletes them from source. It takes five arguments: source_folder, which is the path of the source folder, dest_folder, which is the path of the destination folder, ext, which is a list of file extensions to filter by, delete_after_copy, which is a boolean that indicates whether to delete the original files after copying, and pattern, which is a regular expression pattern to match file names against.
LOG_PATH: a global variable that represents the path of the log file that collects data of the copying process.
LOG_DEBUG_PATH: a global variable that represents the path of the debug log file that collects extended info with names of copied files.

"""


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
            f.write(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}\n")


def copy_files_job():
    """Function to copy files"""
    copy_files_in_folders()
    write_to_debug_log(LOG_DEBUG_PATH, ["Copy job is running"])


def run_copy_job():
    """Scheduled the copy job to run at a specific time"""
    config = read_config()
    scheduled = config.get("scheduled_every_15_minutes")
    scheduled_time_str = config.get("scheduled_on_time")
    
    if scheduled:
        if scheduled_time_str:
            try:
                hour, minute = [int(x) for x in scheduled_time_str.split(":")]
                if hour >= 0 and hour < 24 and minute >= 0 and minute < 60:
                # Schedule job to run at the specified time
                    schedule.every().day.at(scheduled_time_str).do(copy_files_job)
                
                    write_to_debug_log(LOG_DEBUG_PATH, [f"Copy job scheduled to run at {scheduled_time_str}"])
                else:
                    print(
                        "Invalid scheduled time format in config file. Using default schedule.")
            except ValueError:
                print("Invalid scheduled time format in config file. Using default schedule.")
        else:
            schedule.every(15).minute.do(copy_files_job)
    
    else:
        # Use default schedule if no scheduled time is specified in config file
        schedule.every(1).hour.do(copy_files_job)
        write_to_debug_log(LOG_DEBUG_PATH, [f"Copy job scheduled to run every hour"])

    while True:
        schedule.run_pending()
        time.sleep(1)
        

def check_and_create_folder(folder_path, log_messages):
    """Checked if folder exists, create it if it doesn't"""
    # print(check_and_create_folder.__doc__)
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            log_messages.append(f"Created folder '{folder_path}'")
        except Exception as e:
            log_messages.append(f"Error creating folder '{folder_path}': {e}")


def get_files(source_dir, ext, pattern=None):
    """
    Returns a list of file paths in the source directory with the given extension.

    Parameters:
    source_dir (str): The path of the source directory.
    ext (list): A list of file extensions to filter by.
    pattern (str): A regular expression pattern to match file names against.

    Returns:
    A list of file paths in the source directory with the given extension and pattern.
    """
    files = []
    for file in os.listdir(source_dir):
        if any(file.endswith(e) for e in ext) and (not pattern or re.search(pattern, file)):
            files.append(os.path.join(source_dir, file))
    return files


def copy_then_remove_files(source_folder, dest_folder, ext, delete_after_copy=False, pattern=None):
    """Copies files with specified extensions and pattern from source directory to destination directory and optionally deletes them from source."""
    # Get file paths in source directory
    file_paths = get_files(source_folder, ext, pattern)

    # Create destination folder if it doesn't exist
    check_and_create_folder(dest_folder, [f"Creating destination folder: {dest_folder}"])

    # Create log folder if it doesn't exist
    check_and_create_folder(LOG_FOLDER, [f"Creating log folder: {LOG_FOLDER}"])

    # Open log file
    with open(LOG_PATH, "a") as log_file:
        log_file.write(f"\n\nCopying process started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Source folder: {source_folder}\n")
        log_file.write(f"Destination folder: {dest_folder}\n")
        log_file.write(f"File extensions: {', '.join(ext)}\n")
        if pattern:
            log_file.write(f"Pattern: {pattern}\n")
        log_file.write("\n")

        # Open debug log file
        with open(LOG_DEBUG_PATH, "a") as debug_log_file:
            debug_log_file.write(f"\n\nCopying process started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            debug_log_file.write(f"Source folder: {source_folder}\n")
            debug_log_file.write(f"Destination folder: {dest_folder}\n")
            debug_log_file.write(f"File extensions: {', '.join(ext)}\n")
            if pattern:
                debug_log_file.write(f"Pattern: {pattern}\n")
            debug_log_file.write("\n")

            # Copy files and log the process
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                dest_file_path = os.path.join(dest_folder, file_name)
                shutil.copy2(file_path, dest_file_path)
                log_file.write(f"Copied {file_name} to {dest_folder}\n")
                debug_log_file.write(f"Copied {file_name} from {source_folder} to {dest_folder}\n")

                # Delete file from source if delete_after_copy is True
                if delete_after_copy:
                    os.remove(file_path)
                    log_file.write(f"Deleted {file_name} from {source_folder}\n")
                    debug_log_file.write(f"Deleted {file_name} from {source_folder}\n")
                    
            # Write end of copy process to log files
            log_file.write(f"\nCopying process ended at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            debug_log_file.write(f"\nCopying process ended at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")



def copy_files_in_folders():
    """Copies files from source folders to destination folders"""
    config = read_config()
    dest_folders = config["destination_folders"]
    log_messages = []
    total_count = 0

    # Get source folders from config
    source_folders = [os.path.expandvars(folder)
                      for folder in config["source_folders"]]

    for source_folder in source_folders:
        if not os.path.exists(source_folder):
            log_messages.append(
                f"Source folder '{source_folder}' does not exist")
            continue

        for folder_name, folder_config in dest_folders.items():
            dest_dir = folder_config["path"]
            check_and_create_folder(dest_dir, log_messages)

            ext = folder_config["file_extensions"]
            delete_after_copy = folder_config["delete_after_copy"]
            pattern = folder_config.get("pattern")

            # Get a list of files in the destination folder
            dest_files = set(os.listdir(dest_dir))

            # Copy files that haven't been copied already
            count = 0
            for file_path in get_files(source_folder, ext, pattern):
                file_name = os.path.basename(file_path)

                if file_name in dest_files:
                    # If the file already exists in the destination folder, skip it
                    continue

                # Copy the file to the destination folder
                dest_path = os.path.join(dest_dir, file_name)
                shutil.copy2(file_path, dest_path)
                count += 1

                # Add the name of the copied file to the set of destination files
                dest_files.add(file_name)

                # If delete_after_copy is True, delete the original file
                if delete_after_copy:
                    os.remove(file_path)

            total_count += count
            log_messages.append(
                f"Copied {count} files from {source_folder} to {dest_dir}")

            # Write filenames to debug log
            debug_log_path = os.path.join(LOG_FOLDER, DEBUG_LOG_FILE_PREFIX + LOG_FILE_NAME_FORMAT.format(
                datetime.datetime.today().strftime("%Y-%m-%d"), "debug"))
            write_to_debug_log(debug_log_path, [
                               f"Copied {count} files from '{source_folder}' to '{dest_dir}'"])

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