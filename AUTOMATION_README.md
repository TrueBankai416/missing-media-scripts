# Media Manager Automation Guide

A comprehensive guide to automating media monitoring tasks using the Media Manager GUI on both Windows and Linux systems.

## Overview

The Media Manager now includes powerful automation features that allow you to schedule the following tasks:

- **Generate Media List**: Scan directories and create timestamped media lists
- **Check for Missing Media**: Compare recent lists and identify missing files
- **Manage File Retention**: Clean up old list files (keep only latest N files)  
- **Check Windows Filename Compatibility**: Detect and report filename issues (does not auto-fix)
- **Run Complete Check**: Execute all operations in sequence

## Quick Start

### 1. Configure Automation Settings

1. **Open the GUI** and go to the **Automation** tab
2. **Enable task automation** by checking the checkbox
3. **Configure individual tasks** or enable "Run Complete Check" to run everything
4. **Set scheduling times** using 24-hour format (e.g., 05:30)
5. **Choose frequency**: Daily or Weekly
6. **Save Automation Settings**

### 2. Apply Scheduled Tasks

1. **Click "Apply Scheduled Tasks"** to create platform-specific scheduled tasks
2. **Check the Status log** for confirmation that tasks were created successfully
3. **Tasks will run automatically** at the specified times

### 3. Monitor and Manage

- **View logs** in the "Logs & Results" tab to see automation results
- **Remove scheduled tasks** using the "Remove All Scheduled Tasks" button
- **Test functionality** with the "Test Task Creation" button

## Detailed Configuration

### Task Configuration Options

#### Individual Tasks
Configure each task independently with different times and frequencies:

```
Generate Media List: Daily at 05:00
Check Missing Media: Daily at 05:30  
Manage File Retention: Daily at 06:00
Check Windows Filenames: Weekly at 06:30
```

#### Complete Check (Recommended)
Enable "Run Complete Check" to execute all operations in sequence at a single time. This overrides individual task settings and is the most efficient approach.

```
Complete Check: Daily at 05:00
(Runs all operations: generate → check missing → manage files → detect filename issues)
Note: Filename checking only detects and reports issues - does NOT automatically rename files
```

### Time Format
- Use **24-hour format**: `HH:MM`
- Examples: `05:30`, `17:45`, `23:00`
- Invalid: `5:30 AM`, `5:30pm`

### Frequency Options
- **Daily**: Runs every day at the specified time
- **Weekly**: Runs once per week (Sunday on Linux, configurable on Windows)

## Platform-Specific Implementation

### Windows (Task Scheduler)
- Uses `schtasks` command-line utility
- Tasks appear in Windows Task Scheduler as "MediaManager_*"
- Requires administrative privileges for task creation
- Tasks run even when user is not logged in (if configured)

### Linux (Cron)
- Uses `crontab` to manage cron jobs
- Jobs are added with "# MediaManager:" comments for identification
- Runs with the user's permissions
- Requires user to be logged in (unless using system cron)

## Important: Filename Checking Behavior

### Detection Only - No Automatic Fixes
The **"Check Windows Filename Compatibility"** task only **detects and reports** filename issues:

- ✅ **Creates reports** of files with Windows naming problems
- ✅ **Saves reports** to `filename_issues/` directory  
- ✅ **Logs issue counts** in automation output
- ❌ **Does NOT automatically rename** any files
- ❌ **Does NOT modify** your media files in any way

### Manual Fix Process
To actually fix filename issues:
1. **Run automation** to detect issues automatically
2. **Review reports** in the "Logs & Results" tab  
3. **Use GUI manually**: Go to "View & Fix Filename Issues" dialog
4. **Review suggestions** and select which fixes to apply
5. **Apply selected fixes** with user verification

This ensures **end user verification** before any files are renamed.

## Advanced Configuration

### Email Notifications
Configure email settings in the "Email Configuration" tab to receive notifications when missing media is detected during automated runs.

### File Retention
Set the number of recent files to keep in the "Main Configuration" tab. Older files are automatically deleted during the "Manage File Retention" task.

### Output Directory Structure
Automated tasks create organized output directories:
```
output_directory/
├── media_lists/           # Generated media lists
├── missing_media/         # Missing media reports  
├── filename_issues/       # Windows filename compatibility reports
└── (legacy files)         # Old format files (root level)
```

## Command-Line Usage (Advanced)

The GUI can also be run in headless mode for direct automation:

```bash
# Individual operations
python media_manager_gui.py --automated-generate-media-list
python media_manager_gui.py --automated-check-missing-media
python media_manager_gui.py --automated-manage-file-retention
python media_manager_gui.py --automated-check-windows-filenames

# Complete check
python media_manager_gui.py --automated-complete-check

# Test automation
python media_manager_gui.py --automated-test
```

## Troubleshooting

### Common Issues

#### "Tasks failed to create"
- **Windows**: Ensure you have administrative privileges
- **Linux**: Verify `crontab` is installed and accessible
- **Both**: Check that Python and script paths are correct

#### "No directories configured"
- Configure scan directories in the "Main Configuration" tab first
- Save the configuration before applying automation

#### "Email notifications not working"
- Configure email settings in the "Email Configuration" tab
- For Gmail: use app passwords, not regular passwords
- Test email configuration manually first

#### "Tasks appear to be created but don't run"
- **Windows**: Check Windows Task Scheduler for error messages
- **Linux**: Check system logs with `journalctl -u crond` or `grep CRON /var/log/syslog`
- **Both**: Verify the Python executable path is correct

### Testing Automation

1. **Use "Test Task Creation"** to verify platform compatibility
2. **Run tasks manually** first to ensure they work correctly  
3. **Check Status logs** for detailed error messages
4. **Start with short test intervals** (e.g., a few minutes) to verify scheduling works

### Viewing Created Tasks

#### Windows
1. Open **Task Scheduler** (`taskschd.msc`)
2. Look for tasks named **"MediaManager_*"** in the Task Scheduler Library
3. View properties, history, and run status

#### Linux  
1. View current crontab: `crontab -l`
2. Look for lines containing **"# MediaManager:"**
3. Check cron logs: `grep CRON /var/log/syslog`

## Security Considerations

### File Permissions
- Ensure the output directory is writable by the user running the tasks
- On Linux, consider using group permissions for shared access

### Network Access
- Email notifications require internet access
- Configure firewall rules if necessary

### Password Security
- Email passwords are stored in plain text in the configuration file
- Consider file permissions: `chmod 600 media_manager_config.json` on Linux
- Use app passwords instead of main account passwords where possible

## Best Practices

### Scheduling Recommendations
1. **Stagger task times** if running individual tasks (5-10 minute intervals)
2. **Use "Complete Check"** for simplicity and efficiency
3. **Schedule during low-usage hours** (early morning) to minimize performance impact
4. **Consider weekly frequency** for large media collections to reduce overhead

### Monitoring and Maintenance
1. **Regularly check logs** for errors or issues
2. **Monitor disk space** in the output directory
3. **Test email notifications** periodically
4. **Review file retention settings** as your collection grows

### Backup and Recovery
1. **Backup configuration files** before making changes
2. **Document your scheduling setup** for easy restoration
3. **Test restore procedures** on a separate system

## Migration from Manual Scripts

If you're migrating from the original manual scripts:

1. **Import existing configuration** by manually copying settings
2. **Test automation thoroughly** before removing manual scripts
3. **Keep manual scripts as backup** until automation is verified
4. **Migrate gradually** by enabling one task at a time

## Support and Troubleshooting

### Log Files
- **GUI Status log**: Real-time feedback during operations
- **Automation output**: Check system logs for scheduled task output
- **Email logs**: Detailed email sending status in the Status log

### Getting Help
- **GitHub Issues**: Report bugs or request features
- **Discord**: Join the community for support and discussions
- **Documentation**: Check other README files for additional information

### Known Limitations
- **macOS**: Not fully supported (may work with manual cron setup)
- **Containers**: Docker/containerized environments may need special configuration
- **Network drives**: May have permissions issues on some systems
- **Long paths**: Windows has path length limitations (may need long path support enabled)

## Example Configurations

### Simple Daily Monitoring
```
Complete Check: Daily at 05:00
Email Notifications: Enabled
File Retention: 30 files
```

### Comprehensive Weekly Check
```
Generate Media List: Daily at 05:00
Check Missing Media: Daily at 05:30
Manage File Retention: Weekly at 06:00
Check Windows Filenames: Weekly at 06:30
Email Notifications: Enabled
File Retention: 100 files
```

### High-Frequency Monitoring
```
Complete Check: Daily at 05:00
Email Notifications: Enabled  
File Retention: 200 files
```

This automation system provides a robust, platform-independent solution for monitoring your media collection with minimal manual intervention.
