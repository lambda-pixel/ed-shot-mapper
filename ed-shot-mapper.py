import os, sys, platform, shutil
import json
from datetime import datetime, timezone
import dateutil.parser
import time


def retrieve_journal(file_path):
    data = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            for line in file:
                entry = json.loads(line)                    
                timestamp = int(dateutil.parser.parse(entry['timestamp']).timestamp())
                    
                # Multiple events with the same timestamp may occur
                if timestamp not in data:
                    data[timestamp] = []

                data[timestamp].append(entry)
            return data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path}: {e}")
    return None


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return int(datetime.fromtimestamp(os.path.getctime(path_to_file), timezone.utc).timestamp())
    else:
        stat = os.stat(path_to_file)
        try:
            return int(datetime.fromtimestamp(stat.st_birthtime, timezone.utc).timestamp())
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return int(datetime.fromtimestamp(stat.st_mtime, timezone.utc).timestamp())


def find_journal_for_screenshot(timestamp, journal_data):
    if timestamp in journal_data:
        for entry in journal_data[timestamp]:
            if entry['event'] == 'Screenshot':
                return entry
    
    return None


def get_system_from_entry(entries):
    for entry in entries:
        if 'StarSystem' in entry:
            return entry['StarSystem']

    return None


def guess_location_from_timestamp(timestamp, journal_data):
    keys = sorted(journal_data.keys())

    last_key = -1
    curr_key_idx = -1

    for i, key in enumerate(keys):
        if key <= timestamp and key > last_key:
            last_key = key
            curr_key_idx = i

    system_found = None

    while curr_key_idx >= 0:
        curr_key = keys[curr_key_idx]
        guessed_system = get_system_from_entry(journal_data[curr_key])

        if guessed_system is not None:
            system_found = guessed_system
            break
        
        curr_key_idx -= 1

    return system_found
    

def main():    
    path_cmdr_log = os.path.join(os.path.expanduser('~'), 'Saved Games', 'Frontier Developments', 'Elite Dangerous')
    path_screenshots = sys.argv[1]

    path_output = 'out'

    # Read and consolidate all journal files
    print(f'Reading commander log files from {path_cmdr_log}')

    journal_data = {}

    for file_name in os.listdir(path_cmdr_log):
        if file_name.startswith("Journal") and file_name.endswith(".log"):
            current_journal = retrieve_journal(os.path.join(path_cmdr_log, file_name))

            for k, v in current_journal.items():
                if k not in journal_data:
                    journal_data[k] = []

                journal_data[k].extend(v)

    # Get all screenshots paths
    path_images = []
    
    if os.path.isfile(path_screenshots):
        path_images = [path_screenshots]
    else:
        for file_name in os.listdir(path_screenshots):
            if file_name.endswith(".jpg") or file_name.endswith(".bmp"):
                path_images.append(os.path.join(path_screenshots, file_name))

    # Link each screenshot to a location
    screenshot_locations = {}

    for path_image in path_images:
        # Try to find a journal for the screenshot
        print(f"Processing screenshot: {path_image}")

        if not os.path.exists(path_image):
            print(f"Screenshot not found: {path_image}")
            continue

        timestamp_screenshot = creation_date(path_image)
        
        e = find_journal_for_screenshot(timestamp_screenshot, journal_data)
        
        if e is None:
            print("\tNo journal entry found for screenshot. Guessing system...")

        system_found = guess_location_from_timestamp(timestamp_screenshot, journal_data)

        if system_found is None:
            print("\tNo system found in journal entries before the screenshot timestamp.")
            continue
        
        print(f"\tGuessed system from timestamp: {system_found}")
        screenshot_locations[path_image] = system_found, timestamp_screenshot

    # Copy each matched screenshot to the output folder
    if not os.path.exists(path_output):
        os.makedirs(path_output)

    for path_image in path_images:
        if path_image in screenshot_locations:
            image_ext = os.path.splitext(path_image)[-1][1:]
            system_name, timestamp = screenshot_locations[path_image]
            system_name = system_name.replace(":", "_").replace("/", "_")

            datestr = datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m-%d %H-%M-%S")

            new_path = os.path.join(path_output, f"{datestr}-{system_name}.{image_ext}")

            if os.path.exists(new_path):
                print(f"File already exists: {new_path}")
                continue

            print(f"Copying {path_image} to {new_path}")
            shutil.copy2(path_image, new_path)
        else:
            print(f"No matching journal entry for {path_image}")


if __name__ == '__main__':
    main()