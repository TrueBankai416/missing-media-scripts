# missing-media-scripts
Scripts to compare lists of media and send an email if something is missing from the list

# How to Use and Schedule Scripts with Cron

## generate_media_list.py
This Python script generates a list of media files (videos) from specified directories and saves them to an output file. To run this script, you need to provide the directories to search for media files and the path to the output file where the list will be saved.

### Usage
```bash
/usr/bin/python3 /path/to/generate_media_list.py -d /your/directory1 /your/directory2 -o /path/to/output/media_list.txt
```

### Scheduling with Cron
To run this script every day at 5 AM, you can add the following line to your crontab:
```bash
0 5 * * * /usr/bin/python3 /path/to/generate_media_list.py -d /your/directory1 /your/directory2 -o /path/to/output/media_list.txt
```

## generate_missing_media_list.py
This Python script identifies missing media files by comparing the most recent media list with the previous one. It requires the directory containing the media list files and the path to the output file where the list of missing media titles will be saved.

### Usage
```bash
/usr/bin/python3 /path/to/generate_missing_media_list.py -m /path/to/media_list_dir -o /path/to/output/missing_media_list.txt
```

### Scheduling with Cron
To run this script every day at 6 AM, you can add the following line to your crontab:
```bash
0 6 * * * /usr/bin/python3 /path/to/generate_missing_media_list.py -m /path/to/media_list_dir -o /path/to/output/missing_media_list.txt
```

## manage_txt_files.sh
This bash script manages the retention of text files in a specified directory, keeping only the latest 100 files. Before running, ensure the script has the correct path to the directory where the text files are stored.

### Usage
Make the script executable:
```bash
chmod +x /path/to/manage_txt_files.sh
```

Run the script:
```bash
/path/to/manage_txt_files.sh
```

### Scheduling with Cron
To run this script every day at 6:05 AM, you can add the following line to your crontab:
```bash
5 6 * * * /path/to/manage_txt_files.sh
```

## Setting up Cron Jobs
1. Open your terminal.
2. Type `crontab -e` to edit your cron jobs.
3. Add the lines provided above for each script to the crontab file.
4. Save and exit the editor. Cron will automatically apply the changes.

Remember to replace `/path/to/` with the actual paths to your scripts and directories.