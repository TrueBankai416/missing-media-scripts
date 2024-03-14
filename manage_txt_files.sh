#!/bin/bash
# This script manages the retention of text files in a specified directory, keeping only the latest 100 files.

#cd lists
# Navigate to the directory where the text files are stored. Uncomment and set the correct path.

ls -tp | grep -v '/$' | tail -n +101 | xargs -I {} rm -- {}
# List all files in the current directory without directories, sort them by modification time in descending order,
# then remove all but the latest 100 files. Adjust the number as needed for different retention requirements.
