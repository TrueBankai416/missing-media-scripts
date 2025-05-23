#!/usr/bin/env python3
import os
import argparse

def generate_media_list(directories, output_file):
    """
    Generates a list of media files from the specified directories and writes them to the output file.

    Args:
    directories (list of str): Directories to search for media files.
    output_file (str): Path to the output file where the list will be saved.
    """
    media_files = []
    for directory in directories:
        for root, dirs, files in os.walk(directory, topdown=True):
            dirs[:] = [d for d in dirs if not d.startswith('.')]  # Ignore hidden directories
            for file in files:
                if file.endswith(('.mp4', '.mkv', '.avi')):
                    media_files.append(os.path.join(root, file))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for file in media_files:
            f.write(f"{file}\n")

def main():
    parser = argparse.ArgumentParser(description="Generate a list of media files.")
    parser.add_argument('-d', '--directories', nargs='+', help='Directories to search for media files.', required=True)
    parser.add_argument('-o', '--output', help='Output file to write the list of media files.', required=True)
    args = parser.parse_args()

    generate_media_list(args.directories, args.output)

if __name__ == "__main__":
    main()
