#!/usr/bin/env python3
"""
Python equivalent of manage_txt_files.sh for Windows compatibility
Manages the retention of text files in a specified directory, keeping only the latest N files.
"""

import os
import glob
import argparse

def manage_files(directory, retention_count=100, file_pattern="*.txt"):
    """
    Manages file retention in the specified directory.
    
    Args:
    directory (str): Directory containing the files to manage.
    retention_count (int): Number of most recent files to keep.
    file_pattern (str): Pattern to match files (default: *.txt).
    
    Returns:
    tuple: (files_kept, files_deleted, error_message)
    """
    try:
        if not os.path.exists(directory):
            return 0, 0, f"Directory does not exist: {directory}"
        
        # Get all files matching the pattern, sorted by modification time (newest first)
        pattern = os.path.join(directory, file_pattern)
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        
        files_kept = min(len(files), retention_count)
        files_deleted = 0
        
        if len(files) > retention_count:
            files_to_delete = files[retention_count:]
            
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    files_deleted += 1
                    print(f"Deleted: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
        
        print(f"File management complete: {files_kept} files kept, {files_deleted} files deleted")
        return files_kept, files_deleted, None
        
    except Exception as e:
        error_msg = f"Error managing files: {e}"
        print(error_msg)
        return 0, 0, error_msg

def main():
    parser = argparse.ArgumentParser(description="Manage file retention in a directory.")
    parser.add_argument('-d', '--directory', help='Directory containing files to manage.', required=True)
    parser.add_argument('-n', '--count', type=int, default=100, help='Number of recent files to keep (default: 100).')
    parser.add_argument('-p', '--pattern', default='*.txt', help='File pattern to match (default: *.txt).')
    
    args = parser.parse_args()
    
    manage_files(args.directory, args.count, args.pattern)

if __name__ == "__main__":
    main()
