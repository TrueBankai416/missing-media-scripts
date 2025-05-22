# Building an Executable (.exe) for Media Manager GUI

This guide explains how to create a standalone executable file that doesn't require Python to be installed on the target machine.

## Quick Build Instructions

### Method 1: Using the Batch Script (Recommended)
1. **Run the build script**:
   ```cmd
   build_exe.bat
   ```
2. **Wait for completion** (may take 2-5 minutes)
3. **Find your executable** at: `dist\MediaManager.exe`

### Method 2: Manual Build
1. **Install PyInstaller**:
   ```cmd
   pip install pyinstaller==6.3.0
   ```

2. **Build the executable**:
   ```cmd
   pyinstaller media_manager_gui.spec
   ```

3. **Find your executable** at: `dist\MediaManager.exe`

## Distribution

### What to Distribute
After building, you can distribute:
- **`dist\MediaManager.exe`** - The main executable (around 15-25 MB)
- **`example_config.json`** - Example configuration (optional)
- **`GUI_README.md`** - User documentation (optional)

### Requirements for End Users
- **Windows 7 or later**
- **No Python installation required**
- **No additional dependencies needed**

## Usage

### Running the Executable
1. **Double-click** `MediaManager.exe`
2. **First run** may take 10-15 seconds (extracting bundled files)
3. **Subsequent runs** will be faster

### Configuration
The executable will create configuration files in the same directory:
- `media_manager_config.json` - Settings file
- `lists\` - Default output directory (auto-created)

## Troubleshooting

### Build Issues

**"Python is not installed or not in PATH"**
- Install Python 3.6+ from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

**"pip is not recognized"**
- Reinstall Python with pip included
- Or install pip manually

**"Build failed with import errors"**
- Make sure all source files are in the same directory
- Try: `pip install --upgrade pyinstaller`

**"Missing modules"**
- The spec file includes all required tkinter modules
- If you get import errors, add missing modules to `hiddenimports` in the spec file

### Runtime Issues

**"The application failed to start"**
- Try running from command prompt to see error messages:
  ```cmd
  MediaManager.exe
  ```

**"Antivirus blocking the executable"**
- Some antivirus software flags PyInstaller executables as suspicious
- Add an exception for the executable in your antivirus settings
- This is a common false positive with PyInstaller

**"Application starts slowly"**
- First run extracts files to temp directory (normal)
- Subsequent runs should be faster
- Consider using `--onedir` instead of `--onefile` for faster startup

**"Configuration not saving"**
- Make sure the executable has write permissions in its directory
- Run as administrator if needed
- Check that the directory isn't read-only

### Advanced Customization

#### Adding an Icon
1. **Create or find** a `.ico` file
2. **Edit** `media_manager_gui.spec`:
   ```python
   icon='path/to/your/icon.ico'
   ```
3. **Rebuild** the executable

#### Reducing File Size
Edit `media_manager_gui.spec` and change:
```python
upx=True  # Compress the executable (slower startup)
```

Or exclude unused modules:
```python
excludes=['module1', 'module2']
```

#### Creating a Folder Distribution (Faster Startup)
Instead of a single .exe file, you can create a folder distribution:

1. **Edit** `media_manager_gui.spec`:
   ```python
   exe = EXE(
       # ... other parameters ...
       onefile=False,  # Add this line
   )
   ```

2. **Rebuild** - This creates a `dist\MediaManager\` folder with:
   - `MediaManager.exe` - Main executable
   - Multiple `.dll` files - Required libraries

This starts faster but requires distributing the entire folder.

## File Sizes

Typical sizes for the built executable:
- **Single file (.exe)**: 15-25 MB
- **Folder distribution**: 20-30 MB (multiple files)

The executable includes:
- Python interpreter
- Tkinter GUI library
- All required standard library modules
- Your application code

## Security Notes

### Code Signing (Optional)
For professional distribution, consider code signing:
1. **Purchase** a code signing certificate
2. **Sign** the executable using Windows SDK tools
3. **This prevents** antivirus false positives and Windows SmartScreen warnings

### Virus Scanning
Before distributing:
1. **Scan** the executable with multiple antivirus engines
2. **Upload** to VirusTotal.com to check for false positives
3. **Consider** submitting to antivirus vendors if flagged incorrectly

## Automation

### Continuous Integration
You can automate builds using GitHub Actions or similar:

```yaml
# Example GitHub Actions workflow
- name: Build executable
  run: |
    pip install pyinstaller==6.3.0
    pyinstaller media_manager_gui.spec
```

### Version Information
To add version info to the executable:
1. **Create** a version file (`.rc` file)
2. **Reference** it in the spec file:
   ```python
   version_file='version.rc'
   ```

This adds properties visible in Windows file explorer.
