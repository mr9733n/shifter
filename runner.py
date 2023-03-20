import subprocess

# subprocess.Popen(["python", "shifter.py"])
while True:
    # Start the script in a new subprocess
    process = subprocess.Popen(["python", "shifter.py"])
    print("File Shifter Started")
    # Wait for the subprocess to finish
    process.communicate()
