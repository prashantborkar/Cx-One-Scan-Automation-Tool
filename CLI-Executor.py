import subprocess
import os
import configparser

def execute_java_scan():
    # Determine the directory path of the current script
    script_dir = os.path.dirname(__file__)

    # Construct the path to application.properties
    properties_file_path = os.path.join(script_dir, 'application.properties')

    # Read paths from application.properties file
    config = configparser.ConfigParser()
    config.read(properties_file_path)
    jar_file = config['FILES']['jar_file']
    properties_file = config['FILES']['properties_file']
    java_bin = config['EXECUTION']['java_bin']

    # Define the command to execute
    command = [java_bin, '-jar', jar_file, properties_file]

    # Open a subprocess and capture stdout and stderr as pipes
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # Print each line from stdout in real-time
    for stdout_line in process.stdout:
        print(stdout_line, end='')

    # Print each line from stderr in real-time
    for stderr_line in process.stderr:
        print(stderr_line, end='')

    # Wait for the process to complete
    exit_code = process.wait()
    print(f"Java process completed with exit code: {exit_code}")

    return exit_code

if __name__ == "__main__":
    try:
        # Execute Java scan
        print("Executing Java scan...")      
        exit_code = execute_java_scan()
        print("Java scan execution complete.")

        # After Java scan completes, execute Process.py
        if exit_code==0:         
            print("Running Process.py...")
            os.system('python Process.py')

    except Exception as e:
        print(f"Error: {str(e)}")

    exit(exit_code)
