
# File Shifter Documentation

This Python script is designed to copy files from source folders to destination folders as specified in a JSON configuration file. It can be run as a service and scheduled to run at a specified time. The following sections detail how to configure and use the script.

## Configuration
Configuration settings are stored in a JSON file named config.json in the same directory as the script. The configuration file contains the following properties:

|Parameter Name |Description | 
--- | --- |
|source_folders| an array of strings representing the source folders to copy files from. |
|destination_folders| an object containing destination folder configurations. |

Each configuration contains the following properties:
|Parameter Name |Description | 
--- | --- |
|path| a string representing the destination folder path. |
|file_extensions| an array of strings representing the file extensions to copy. |
|delete_after_copy| a boolean indicating whether to delete the files from the source after they have been copied.
|pattern| (optional) a regular expression pattern that the file names must match to be copied. |
|scheduled_on_time| (optional) a string representing the time at which to run the copy job on a schedule. The format should be "HH:MM". |
* Note: Destination folder paths are modified based on the operating system being used. On Windows, the path is prefixed with "C:", while on other operating systems, it is prefixed with "/".

## Functions
The script contains several functions that are used to copy files and log messages. These functions are described below.

|Parameter Name |Description | 
--- | --- |
|read_config() |This function reads the configuration file and returns a dictionary containing the configuration settings. |
|check_and_create_folder(folder_path, log_messages)|This function checks if the specified folder exists and creates it if it doesn't. It appends log messages to the log_messages list.|
|write_to_log(log_path, messages)|This function writes the log messages to a log file at the specified path.|
|copy_then_remove_files(source_dir, dest_dir, ext, delete_after_copy, pattern=None)|This function copies files from the source directory to the destination directory and optionally deletes them from the source. It returns the number of files copied.|
|copy_files_in_folders()|This function iterates over the source folders and destination folders defined in the configuration file and calls |
|copy_then_remove_files()| for each combination. It also writes log messages to the log file.|
|run_copy_job()|This function schedules the copy_files_in_folders() function to run at a specific time, as defined in the configuration file. If no specific time is defined, it runs the function every hour.|
|signal_handler(signal, frame)|This function is a signal handler that catches the interrupt signal and performs any necessary cleanup before exiting the script.|
|Running the Script|To run the script, simply execute it with Python from the command line. The script will run once and copy any files that match the configuration settings. To run the script as a service and schedule it to run at a specific time, execute the script with Python and leave it running. It will continue to run and copy files according to the schedule.

* To stop the script, press CTRL + C to send an interrupt signal. The script will catch the signal and perform any necessary cleanup before exiting.

## Configuration

config.json file template:
```
{
  "source_folders": [
    "%USERPROFILE%/Downloads",
    "C:/9834758345hf73"
  ],
  "destination_folders": {
    "folder1": {
      "path": "C:/9834758345hf73/temp",
      "file_extensions": [".torrent"],
      "delete_after_copy": false,
	  "pattern": null 
    },
    "folder2": {
      "path": "C:/9834758345hf73/temp/folder2",
      "file_extensions": [".txt", ".csv", ".pdf"],
      "delete_after_copy": false,
	  "pattern": null
    },
    "folder3": {
      "path": "C:/9834758345hf73/temp/folder3",
      "file_extensions": [".zip"],
      "delete_after_copy": true,
      "pattern": null
    }
  },
  "scheduled_on_time": null
}
```
- Where could be: 
    - "%USERPROFILE%/Downloads" uses for windows 
    - "scheduled_on_time": "HH:MM"
    - "pattern": "^IMG_[0-9]+\\.jpg$"