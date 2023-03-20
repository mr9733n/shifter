import os
from pathlib import Path
import shutil
import re
import datetime
import shifter_utils
from shifter_utils import LOG_FOLDER, LOG_FILE_PREFIX, DEBUG_LOG_FILE_PREFIX, LOG_FILE_EXTENSION, LOG_FILE_NAME_FORMAT, LOG_DEBUG_PATH, LOG_PATH


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
    """
    Copies files with specified extensions and pattern from source directory to destination directory 
    and optionally deletes them from source.
    """
    log_messages = "Creating destination folder..."
    # Create a set to store the names of the files that have already been copied
    copied_files = set()

    # Check if the destination folder exists, and create it if it doesn't
    check_and_create_folder(dest_folder, log_messages)

    # Check if there is already a log file in the destination folder
    log_path = os.path.join(dest_folder, "log.txt")
    if os.path.exists(log_path):
        # If there is, read the file and add the names of the copied files to the set
        with open(log_path, "r") as f:
            for line in f:
                file_name = line.strip()
                if file_name:
                    copied_files.add(file_name)

    count = 0
    for file_path in get_files(source_folder, ext, pattern):
        file_name = os.path.basename(file_path)
        if file_name in copied_files:
            # If the file has already been copied, skip it
            continue

        # Copy the file to the destination folder
        dest_path = os.path.join(dest_folder, file_name)
        shutil.copy2(file_path, dest_path)
        count += 1

        # Add the name of the copied file to the set
        copied_files.add(file_name)

        # If delete_after_copy is True, delete the original file
        if delete_after_copy:
            os.remove(file_path)

    # Write the names of the copied files to the log file
    with open(log_path, "w") as f:
        for file_name in copied_files:
            f.write(file_name + "\n")

    return count


def copy_files_in_folders():
    """Copies files from source folders to destination folders"""
    config = shifter_utils.read_config()
    dest_folders = config["destination_folders"]
    log_messages = []
    total_count = 0

    # Get source folders from config
    source_folders = [os.path.expandvars(folder) for folder in config["source_folders"]]

    for source_folder in source_folders:
        if not os.path.exists(source_folder):
            log_messages.append(f"Source folder '{source_folder}' does not exist")
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
            log_messages.append(f"Copied {count} files from {source_folder} to {dest_dir}")

            # Write filenames to debug log
            debug_log_path = os.path.join(LOG_FOLDER, DEBUG_LOG_FILE_PREFIX + LOG_FILE_NAME_FORMAT.format(datetime.datetime.today().strftime("%Y-%m-%d"), "debug"))
            shifter_utils.write_to_debug_log(debug_log_path, [f"Copied {count} files from '{source_folder}' to '{dest_dir}'"])

    # write all log messages to file
    shifter_utils.write_to_log(LOG_PATH, log_messages)
    shifter_utils.write_to_debug_log(LOG_DEBUG_PATH, log_messages)

    # write total count to log
    print(f"Total files copied: {total_count}")
    shifter_utils.write_to_log(LOG_PATH, [f"Total files copied: {total_count}"])
    shifter_utils.write_to_debug_log(LOG_DEBUG_PATH, [f"Total files copied: {total_count}"])


if __name__ == '__main__':
    print("Started...")
    logs_dir = Path.cwd() / "Logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    shifter_utils.write_to_log(LOG_PATH, [f"Service started..."])
    shifter_utils.write_to_debug_log(LOG_DEBUG_PATH, [f"Service started..."])
    copy_files_in_folders()
    shifter_utils.run_copy_job()