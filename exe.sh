#!/bin/bash

# Define the log file
LOG_FILE="logs/nohup_output.log"

# Run the Python script as a module with nohup and store the process ID
nohup python3 -m app.crawl > "$LOG_FILE" 2>&1 &

PID=$!
echo "current process ID: $PID" > pid.txt

echo "Script started in background."
echo "Logs can be found in $LOG_FILE"
echo "PID: $PID (saved in pid.txt)"