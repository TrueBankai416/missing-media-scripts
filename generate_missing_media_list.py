#!/usr/bin/env python3
import os
import argparse
import glob
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

def load_expected_titles(expected_titles_file):
    """
    Loads the expected media titles from a file.

    Args:
    expected_titles_file (str): Path to the file containing expected media titles.

    Returns:
    set of str: A set containing the expected media titles.
    """
    with open(expected_titles_file, 'r') as f:
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

    # Load titles from both files
    def load_titles_from_file(file_path):
        with open(file_path, 'r') as f:
            return set(f.read().splitlines())

    most_recent_titles = load_titles_from_file(most_recent_file)
    second_most_recent_titles = load_titles_from_file(second_most_recent_file)

    # Find missing titles
    missing_titles = second_most_recent_titles - most_recent_titles

    if missing_titles:
        with open(output_file, 'w') as f:
            for title in sorted(missing_titles):
                f.write(f"{title}\n")
        send_email("Missing Media Files", "The following media files are missing:\n\n" + '\n'.join(sorted(missing_titles)))
        print(f"Missing titles written to {output_file}")
    else:
        print("No titles are missing.")

def main():
    parser = argparse.ArgumentParser(description="Generate a list of missing media titles.")
    parser.add_argument('-m', '--media-list-dir', help='Directory containing the media list files.', required=True)
    parser.add_argument('-o', '--output', help='Output file to write the list of missing media titles.', required=True)
    args = parser.parse_args()

    generate_missing_media_list(args.media_list_dir, args.output)

def send_email(subject, body):
    sender_name = "SENDER_NAME_HERE"
    sender_email = "SENDER_EMAIL_HERE"
    receiver_email = "RECEIVER_EMAIL_HERE"
    password = "PASSWORD_HERE"

    message = MIMEMultipart()
    message["From"] = formataddr((sender_name, sender_email))
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP('smtp.server.com', 587)  # Use the correct SMTP server and port
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()
    #return media_files #this causes errors

if __name__ == "__main__":
    main()
