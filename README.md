# missing-media-scripts
Scripts to compare lists of media and send an email if something is missing from the list

# Notice
You will first have to open `generate_missing_media_list.py` and configure your email.

The `generate_missing_media_list.py` script will only detect a change if the file name or path changes.

# Purpose
The purpose of the `generate_media_list.py` script is to scan the desired directories for `MKV,MP4, and AVI` files and then generate a list with the files and their absolute paths every morning at 5am (if using cron).

The purpose of the `generate_missing_media.py` script is to compare the last two lists created by the `generate_media_list.py` script. If there is a missing entry in the most recent list, it will generate another list with the names and absolute paths of the missing media files. From there it will also email you the list of missing content (this script will run every morning at 6am if using cron).

The purpose of the `manage_txt_files.sh` is to rotate the lists and only allow 100 lists to exist on the system. (this script will run every morning at 6:05am if using cron).

# Discord
https://discord.com/channels/1217932881301737523/1217933464955785297

# How to Use and Schedule Scripts with Cron

## generate_media_list.py
This Python script generates a list of media files (videos) from specified directories and saves them to an output file. To run this script, you need to provide the directories to search for media files and the path to the output file where the list will be saved.

### Usage
```bash
/path/to/generate_media_list.py -d /your/directory1 /your/directory2 -o /path/to/output/media_list.txt
```

### Scheduling with Cron
To run this script every day at 5 AM, you can add the following line to your crontab:
```bash
0 5 * * * /path/to/generate_media_list.py -d /your/directory1 /your/directory2 -o /path/to/output/media_list.txt
```

## generate_missing_media_list.py
This Python script identifies missing media files by comparing the most recent media list with the previous one. It requires the directory containing the media list files and the path to the output file where the list of missing media titles will be saved.

### Usage
```bash
/path/to/generate_missing_media_list.py -m /path/to/media_list_dir -o /path/to/output/missing_media_list.txt
```

### Scheduling with Cron
To run this script every day at 6 AM, you can add the following line to your crontab:
```bash
0 6 * * * /path/to/generate_missing_media_list.py -m /path/to/media_list_dir -o /path/to/output/missing_media_list.txt
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

##For reference
Here is my setup
![image](https://github.com/TrueBankai416/missing-media-scripts/assets/97103466/f47e7c33-06b4-42cd-9107-d251a88d7656)

![image](https://github.com/TrueBankai416/missing-media-scripts/assets/97103466/bea11c19-7673-401b-abe9-044c75d1362d)

![image](https://github.com/TrueBankai416/missing-media-scripts/assets/97103466/c21528a3-6528-4520-b328-d81b9fc38804)

![image](https://github.com/TrueBankai416/missing-media-scripts/assets/97103466/8fa4114a-d6cc-4646-b7f4-5c58d723fe38)

![email](https://github.com/TrueBankai416/missing-media-scripts/assets/97103466/a84c473e-fbb6-44a9-8430-26a8da50ff83)



