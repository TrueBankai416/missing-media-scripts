# Media Manager GUI for Windows

A user-friendly Windows GUI application that simplifies the process of monitoring media files and detecting missing content. This GUI wraps the existing command-line scripts in an intuitive interface.

## Features

- **Easy Directory Management**: Add/remove directories to scan for media files with a simple GUI
- **Automated Media List Generation**: Scan directories and generate timestamped media lists
- **Missing Media Detection**: Compare recent lists to identify missing files
- **Email Notifications**: Automatically send email alerts when missing media is detected
- **File Retention Management**: Automatically manage old list files (keep only the latest N files)
- **Configuration Persistence**: Save all settings between sessions
- **Real-time Logging**: View operation status and results in real-time
- **File Management**: View and browse generated lists and results

## Installation

### Prerequisites
- Python 3.6 or later
- Windows operating system
- Internet connection (for email notifications)

### Setup Instructions

1. **Download or Clone the Repository**
   ```bash
   git clone https://github.com/TrueBankai416/missing-media-scripts.git
   cd missing-media-scripts
   ```

2. **Run the GUI**
   ```bash
   python media_manager_gui.py
   ```

   Or double-click the `run_gui.bat` file (if created)

## Quick Start Guide

### 1. Initial Configuration

When you first run the application:

1. **Go to the Configuration tab**
2. **Add Scan Directories**:
   - Click "Add Directory" to select folders containing your media files
   - Add multiple directories as needed
   - Remove directories using "Remove Selected"

3. **Set Output Directory**:
   - Choose where to save the generated lists
   - Default: `lists` folder in the current directory

4. **Configure Email (Optional)**:
   - Set up email notifications for missing media alerts
   - Required fields: Sender Email, Receiver Email, Password, SMTP Server
   - Default SMTP: Gmail (smtp.gmail.com:587)

5. **Set File Retention**:
   - Choose how many old list files to keep (default: 100)

6. **Click "Save Configuration"**

### 2. Basic Operations

#### Generate Media List
- Click "Generate Media List" in the Main tab
- This scans all configured directories for .mp4, .mkv, and .avi files
- Creates a timestamped list file

#### Check for Missing Media
- Click "Check for Missing Media"
- Compares the two most recent media lists
- Identifies files that were in the previous list but missing from the current list
- Sends email notification if configured

#### Run Complete Check
- Click "Run Complete Check" to perform all operations in sequence:
  1. Generate new media list
  2. Check for missing media
  3. Clean up old files

### 3. Viewing Results

Use the **Logs & Results** tab to:
- View all generated list files
- Read file contents
- Open the output folder in Windows Explorer
- Monitor file creation timestamps

## Configuration Details

### Email Setup

For Gmail users:
1. **Enable 2-Factor Authentication** on your Google account
2. **Create an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. **Use the app password** (not your regular password) in the GUI

For other email providers:
- Update the SMTP server and port in the configuration
- Common SMTP settings:
  - **Outlook/Hotmail**: smtp-mail.outlook.com:587
  - **Yahoo**: smtp.mail.yahoo.com:587
  - **Gmail**: smtp.gmail.com:587

### Directory Scanning

The application searches for these file types:
- `.mp4` - MPEG-4 video files
- `.mkv` - Matroska video files  
- `.avi` - Audio Video Interleave files

Hidden directories (starting with '.') are automatically ignored.

### File Naming Convention

Generated files use timestamps in the format: `YYYYMMDD_HHMMSS`

- **Media Lists**: `media_list_20240522_143022.txt`
- **Missing Media**: `missing_media_20240522_143022.txt`

## Automation Options

### Windows Task Scheduler

To automate the media checking process:

1. **Open Task Scheduler** (Start → Task Scheduler)
2. **Create Basic Task**
3. **Set Trigger**: Daily at your preferred time
4. **Set Action**: Start a program
5. **Program**: `python.exe`
6. **Arguments**: `path\to\media_manager_gui.py --auto-run`
7. **Start in**: Directory containing the scripts

Note: The `--auto-run` flag is a future enhancement for headless operation.

### Batch File Automation

Create a batch file to run operations:

```batch
@echo off
cd /d "C:\path\to\missing-media-scripts"
python media_manager_gui.py
pause
```

## Troubleshooting

### Common Issues

1. **"No module named 'tkinter'"**
   - Ensure Python was installed with tkinter support
   - On some Linux distributions: `sudo apt-get install python3-tk`

2. **Email sending fails**
   - Verify email credentials and app password
   - Check firewall/antivirus settings
   - Ensure SMTP server and port are correct

3. **Permission errors**
   - Run as administrator if accessing system directories
   - Check folder permissions for output directory

4. **No files found**
   - Verify directory paths are correct
   - Check that directories contain .mp4, .mkv, or .avi files
   - Ensure directories are accessible

### Log Messages

The application provides detailed logging in the Status section:
- **Green messages**: Successful operations
- **Red messages**: Errors that need attention
- **Timestamps**: All operations are timestamped for tracking

## File Structure

```
missing-media-scripts/
├── media_manager_gui.py          # Main GUI application
├── generate_media_list.py        # Core media scanning functionality
├── generate_missing_media_list.py # Missing media detection
├── manage_txt_files.sh           # Original bash script (Linux/Mac)
├── media_manager_config.json     # GUI configuration (auto-generated)
├── lists/                        # Default output directory
│   ├── media_list_*.txt          # Generated media lists
│   └── missing_media_*.txt       # Missing media reports
└── README.md                     # Original documentation
```

## Differences from Command Line Scripts

The GUI provides several enhancements over the original command-line scripts:

1. **Persistent Configuration**: Settings are saved between sessions
2. **Real-time Feedback**: Status updates and progress indication
3. **File Management**: Built-in file browser and viewer
4. **Error Handling**: User-friendly error messages
5. **Cross-platform File Management**: Python-based file retention instead of bash script
6. **Email Configuration**: Built-in email setup and testing

## Support

For issues, questions, or feature requests:
- **GitHub Issues**: Create an issue in the repository
- **Discord**: Join the community discord at the link in the main README

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
