# Media Manager - Missing Media Detection System

A comprehensive media file monitoring system that tracks your media collection, detects missing files, and sends notifications when content goes missing. Available as both a user-friendly GUI application and command-line tools.

## Features

- 🔍 **Media File Scanning**: Automatically scan directories for video files (.mp4, .mkv, .avi)
- 📊 **Missing Media Detection**: Compare recent scans to identify missing files
- 📧 **Email Notifications**: Get alerted when media files go missing
- 🗂️ **File Management**: Automatic retention management (keep only N recent lists)
- 🖥️ **Cross-Platform GUI**: Easy-to-use graphical interface for Windows and Linux
- ⚙️ **Automation Support**: Schedule tasks with Windows Task Scheduler or Linux cron
- 🛠️ **Windows Compatibility**: Check and fix Windows filename issues
- 💻 **Headless Operation**: Run without GUI for servers and automated systems

## Quick Start

### Windows Users (Recommended)

**Option 1: Standalone Executable** (See `BUILD_EXECUTABLE.md`)
1. Build or download the `.exe` file
2. Run `MediaManager.exe` directly (no Python installation required)


**Option 2: GUI Application**
1. Download or clone this repository
2. Double-click `run_gui.bat` to start the GUI
3. Configure your media directories in the "Main Configuration" tab
4. Click "Run Complete Check" to start monitoring


### Linux Users

**GUI Mode:**
```bash
# Install tkinter if needed (Ubuntu/Debian)
sudo apt-get install python3-tk

# Clone and run
git clone https://github.com/TrueBankai416/missing-media-scripts.git
cd missing-media-scripts
python3 media_manager_gui.py
```

**Command Line Mode:**
```bash
# Generate media list
python3 generate_media_list.py -d /path/to/media1 /path/to/media2 -o media_list.txt

# Check for missing media
python3 generate_missing_media_list.py -m /path/to/lists -o missing_media.txt

# Manage file retention
python3 manage_files.py -d /path/to/lists -n 100
```

### Headless/Server Systems

For servers or automated systems without GUI:

```bash
# Complete automated check
python3 media_manager_gui.py --automated-complete-check

# Individual operations
python3 media_manager_gui.py --automated-generate-media-list
python3 media_manager_gui.py --automated-check-missing-media
python3 media_manager_gui.py --automated-manage-file-retention
python3 media_manager_gui.py --automated-check-windows-filenames
```

## Installation

### Requirements

- **Python 3.6+** (not required for Windows .exe version)
- **tkinter** (for GUI - usually included with Python)
- **Internet connection** (for email notifications)

### Dependencies

This project uses only Python standard library modules:
- `tkinter` (GUI)
- `os`, `json`, `threading`, `datetime`, `glob`
- `smtplib`, `email` (notifications)
- `pathlib`, `argparse`

No external packages required!

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/TrueBankai416/missing-media-scripts.git
   cd missing-media-scripts
   ```

2. **For GUI usage:** Run the appropriate launcher for your system
3. **For command-line usage:** Use the individual Python scripts directly

## Configuration

### Using the GUI (Recommended)

1. **Launch the GUI** using `python3 media_manager_gui.py` or `run_gui.bat`
2. **Configure scan directories** in the "Main Configuration" tab
3. **Set up email notifications** in the "Email Configuration" tab (optional)
4. **Configure automation** in the "Automation" tab (optional)
5. **Save settings** - configuration is automatically persisted

### Manual Configuration

Create a `media_manager_config.json` file based on `example_config.json`:

```json
{
    "scan_directories": [
        "/path/to/movies",
        "/path/to/tv-shows"
    ],
    "output_directory": "/path/to/output",
    "file_extensions": {
        "media": [".mp4", ".mkv", ".avi"],
        "additional": [".mov", ".wmv", ".flv", ".webm"]
    },
    "email": {
        "enabled": true,
        "sender_email": "your-email@gmail.com",
        "receiver_email": "alerts@example.com",
        "password": "your-app-password",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587
    },
    "file_retention_count": 100
}
```

### Email Setup

**For Gmail:**
1. Enable 2-Factor Authentication
2. Create an App Password (Google Account → Security → 2-Step Verification → App passwords)
3. Use the app password (not your regular password) in the configuration

**For other providers:**
- **Outlook/Hotmail**: `smtp-mail.outlook.com:587`
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **Gmail**: `smtp.gmail.com:587`

## Automation

### Using the GUI Automation (Recommended)

1. **Open the Automation tab** in the GUI
2. **Enable automation** and configure task scheduling
3. **Click "Apply Scheduled Tasks"** to create platform-specific scheduled tasks
4. **Choose between:**
   - **Individual tasks** with different schedules
   - **Complete Check** (recommended) - runs all operations in sequence

### Manual Scheduling

**Linux (cron):**
```bash
# Edit crontab
crontab -e

# Add these lines for daily automation at 5 AM
0 5 * * * cd /path/to/missing-media-scripts && python3 media_manager_gui.py --automated-complete-check
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 5:00 AM
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `path\to\media_manager_gui.py --automated-complete-check`
7. Start in: Directory containing the scripts

## Usage Examples

### Basic Operations

**Scan directories and generate media list:**
```bash
python3 generate_media_list.py -d /home/user/Movies /home/user/TV -o media_list.txt
```

**Check for missing media:**
```bash
python3 generate_missing_media_list.py -m /path/to/lists -o missing_media.txt
```

**Clean up old files:**
```bash
python3 manage_files.py -d /path/to/lists -n 50
```

**Check Windows filename compatibility:**
```bash
python3 windows_filename_validator.py -i media_list.txt -o filename_report.txt
```

### GUI Automation Commands

**Run complete check (all operations):**
```bash
python3 media_manager_gui.py --automated-complete-check
```

**Individual operations:**
```bash
python3 media_manager_gui.py --automated-generate-media-list
python3 media_manager_gui.py --automated-check-missing-media
python3 media_manager_gui.py --automated-manage-file-retention
python3 media_manager_gui.py --automated-check-windows-filenames
```

**Test automation setup:**
```bash
python3 media_manager_gui.py --automated-test
```

## File Structure

```
missing-media-scripts/
├── media_manager_gui.py          # Main GUI application
├── generate_media_list.py        # Core media scanning
├── generate_missing_media_list.py # Missing media detection
├── manage_files.py               # File retention management
├── windows_filename_validator.py # Windows compatibility checker
├── email_utils.py                # Email notification system
├── run_gui.bat                   # Windows GUI launcher
├── media_manager_config.json     # Configuration file (auto-generated)
├── example_config.json           # Example configuration
├── requirements.txt              # Python dependencies (for building .exe)
├── AUTOMATION_README.md          # Detailed automation guide
├── GUI_README.md                 # Detailed GUI documentation
├── BUILD_EXECUTABLE.md           # Instructions for building .exe
└── lists/                        # Default output directory
    ├── media_list_*.txt          # Generated media lists
    └── missing_media_*.txt       # Missing media reports
```

## Troubleshooting

### Common Issues

**"No module named 'tkinter'"**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL/Fedora
sudo yum install tkinter
# or
sudo dnf install python3-tkinter
```

**Email sending fails**
- Verify email credentials and app password
- Check firewall settings
- Ensure SMTP server and port are correct
- For Gmail: Use app passwords, not regular passwords

**Permission errors**
- Ensure read access to media directories
- Ensure write access to output directory
- On Windows: Run as administrator if accessing system directories

**No files found**
- Verify directory paths are correct
- Check that directories contain supported file types (.mp4, .mkv, .avi)
- Ensure directories are accessible and not hidden

### Platform-Specific Notes

**Windows:**
- Use backslashes in paths or raw strings: `r"C:\Users\Name\Videos"`
- Some antivirus software may interfere with file operations
- Long path support may need to be enabled for very long filenames

**Linux:**
- Hidden directories (starting with '.') are automatically ignored
- Ensure proper file permissions for output directories
- For system-wide automation, consider using `/etc/cron.d/`

**Headless Systems:**
- Use `--automated-*` flags for GUI-less operation
- Email notifications are especially useful for monitoring
- Consider using `screen` or `tmux` for long-running operations

## Support and Community

- **GitHub Issues**: Report bugs or request features
- **Discord**: Join the community at https://discord.com/channels/1217932881301737523/1217933464955785297
- **Documentation**: Check `AUTOMATION_README.md` and `GUI_README.md` for detailed guides

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Changelog

**Recent improvements:**
- Added cross-platform GUI with automation support
- Implemented Windows filename compatibility checking
- Enhanced email notification system
- Added headless operation modes
- Improved file retention management
- Added comprehensive configuration system
