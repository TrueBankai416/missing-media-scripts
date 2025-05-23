#!/usr/bin/env python3
import os
import argparse
import glob
from email_utils import send_missing_media_email, create_email_config_hardcoded

def load_expected_titles(expected_titles_file):
    """
    Loads the expected media titles from a file.

    Args:
    expected_titles_file (str): Path to the file containing expected media titles.

    Returns:
    set of str: A set containing the expected media titles.
    """
    with open(expected_titles_file, 'r', encoding='utf-8') as f:
        return set(f.read().splitlines())

def find_two_most_recent_media_lists(directory, pattern):
    """
    Finds the two most recent media list files in the specified directory matching the given pattern.

    Args:
    directory (str): The directory to search in.
    pattern (str): The pattern to match filenames.

    Returns:
    tuple of str: The paths to the most recent and the second most recent media list files.
    """
    files = sorted(glob.glob(os.path.join(directory, pattern)), key=os.path.getmtime, reverse=True)
    if len(files) < 2:
        return None, None
    return files[0], files[1]  # Return the most recent and the second most recent

def generate_missing_media_list(media_list_dir, output_file):
    """
    Compares the two most recent media lists to identify titles present in the second most recent list but missing in the most recent list.

    Args:
    media_list_dir (str): Directory containing the media list files.
    output_file (str): Path to the output file where the list of missing media titles will be saved.
    """
    most_recent_file, second_most_recent_file = find_two_most_recent_media_lists(media_list_dir, 'media_list_*.txt')

    # Check if we have enough files to compare
    if not most_recent_file or not second_most_recent_file:
        error_msg = f"Error: Need at least 2 media list files in {media_list_dir} to compare"
        print(error_msg)
        print("Please run generate_media_list.py at least twice to create comparison files")
        return False

    # Load titles from both files
    def load_titles_from_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return set(f.read().splitlines())
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return set()

    most_recent_titles = load_titles_from_file(most_recent_file)
    second_most_recent_titles = load_titles_from_file(second_most_recent_file)

    if not most_recent_titles and not second_most_recent_titles:
        print("Error: Could not load any media lists")
        return False

    # Find missing titles
    missing_titles = second_most_recent_titles - most_recent_titles

    if missing_titles:
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for title in sorted(missing_titles):
                    f.write(f"{title}\n")
            print(f"Missing titles written to {output_file}")
            
            # Attempt to send email notification
            print("Attempting to send email notification...")
            email_sent = send_missing_media_email(missing_titles)
            if not email_sent:
                print("Note: Email notification failed. Check your email configuration in email_utils.py")
        except Exception as e:
            print(f"Error writing output file {output_file}: {e}")
            return False
    else:
        print("No titles are missing.")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Generate a list of missing media titles.")
    parser.add_argument('-m', '--media-list-dir', help='Directory containing the media list files.', required=True)
    parser.add_argument('-o', '--output', help='Output file to write the list of missing media titles.', required=True)
    args = parser.parse_args()

    generate_missing_media_list(args.media_list_dir, args.output)


if __name__ == "__main__":
    main()
