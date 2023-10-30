import os
import re
from collections import defaultdict
from PIL import Image, ExifTags
from pathlib import Path
from dateutil import parser

def clean_folder(path: str):
    # TODO: Loop folders
    for dir_name, sub_dir_names, file_names in os.walk(path):
        files_to_keep = set(file_names[:])
        files_to_remove = []

        files_to_keep, files_removed = remove_json_files(files_to_keep)
        files_to_remove.append(files_removed)

        files_to_keep, files_removed = remove_duplicate_files(files_to_keep)
        files_to_remove.append(files_removed)

        files_to_keep, files_removed = remove_unwanted_hyphenated_files(files_to_keep)
        files_to_remove.append(files_removed)

        ensure_date_set(dir_name, files_to_keep)

        print("Script would keep:")
        print([f'{f}' for f in files_to_keep])

        print("Script would remove:")
        print([f'{f}' for f in files_to_remove])

        # TODO: Remove files to remove

def remove_json_files(files:list[str]) -> tuple[list[str], list[str]]:
    """Remove JSON files from the list.

    Returns:
        tuple[list[str], list[str]]: (files to keep, removed files)
    """
    files_to_keep = [file_name for file_name in files if not file_name.endswith('.json')]
    files_removed = [f for f in files if f not in files_to_keep]
    return (files_to_keep, files_removed)

def remove_duplicate_files(files:list[str]) -> tuple[list[str], list[str]]:
    """Remove duplicate files from the list.

    Checks for files that have a parenthesized number in the name like (1)
    and removes them if there is a file without the parenthesized number.

    Returns:
        tuple[list[str], list[str]]: (files to keep, removed files)
    """
    files_to_keep = files
    files_removed = []

    numbered_files = {file_name for file_name in files if re.search(r'\(\d+\)', file_name)}
    for numbered_file in numbered_files:
        unnumbered_file = re.sub(r'\(\d+\)', '', numbered_file)
        if unnumbered_file in files: # TODO: Also check content hash?
            files_removed.append(numbered_file)
            files_to_keep.remove(numbered_file)
    
    return (files_to_keep, files_removed)

def remove_unwanted_hyphenated_files(files:list[str]) -> tuple[list[str], list[str]]:
    """Remove hyphenated files from the list.

    Finds all files with hyphenations and uses a combination of whitelist
    and blacklist hyphenations to remove or keep files. If the hyphenation
    is not on either list, it prompts for a decision.

    Returns:
        tuple[list[str], list[str]]: (files to keep, removed files)
    """
    files_to_keep = files
    files_removed = []

    hyphenations_to_keep = ['MOVIE', 'PANO']
    hyphenations_to_remove = ['TWINKLE', 'SNOW', 'edited', 'PANO-edited']

    # Build a dict of hyphenated keys -> list of file names
    hyphenated_files = defaultdict(list)
    for file_name in files:
        match = re.search(r'-(\D+)\.', file_name)
        if match is None:
            continue
        hyphenated_files[match.groups()[0]].append(file_name)

    for hyphenation in hyphenated_files.keys():
        # Keep files where hyphenation is on whitelist
        if hyphenation in hyphenations_to_keep:
            continue
        # Remove files where hyphenation is on blacklist
        elif hyphenation in hyphenations_to_remove:
            for hyphenated_file in hyphenated_files[hyphenation]:
                files_removed.append(hyphenated_file)
                files_to_keep.remove(hyphenated_file)
        else:
            # Prompt to determine whether to keep or remove
            response = input(f'Keep items with {hyphenation} in name? (y/n):\n')
            if response.lower() == 'y':
                continue
            else:
                for hyphenated_file in hyphenated_files[hyphenation]:
                    files_removed.append(hyphenated_file)
                    files_to_keep.remove(hyphenated_file)

    return (files_to_keep, files_removed)

def ensure_date_set(dir_name: str, files: list[str]) -> None:
    image_extensions = ('.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.raw')
    image_files = (file_name for file_name in files if file_name.endswith(image_extensions))

    for file_name in image_files:
        # Open image and read EXIF
        image_path = os.path.join(dir_name, file_name)
        
        image = Image.open(image_path)
        image_exif = image.getexif()

        date_tags = [ExifTags.Base.DateTime, ExifTags.Base.DateTimeOriginal, ExifTags.Base.DateTimeDigitized]
        
        # Only update EXIF if no date tag is set
        if not any(tag for tag in date_tags if tag in image_exif):
            # Strip any suffixes from name
            file_name_as_date = Path(file_name)
            while file_name_as_date.suffix:
                file_name_as_date = file_name_as_date.with_suffix('')
            file_name_as_date = str(file_name_as_date)

            # Try to remove everything other than numbers and separators between numbers
            file_name_as_date = re.sub(r'[^0-9\:\-]|-\D', '', file_name_as_date)

            # Attempt to interpret name as a date and time
            try:
                date_time = parser.parse(file_name_as_date)
            except ValueError:
                print(f'Unable to determine datetime for f{file_name}.')
                print(f'Please specify a value in "YYYY-MM-DD hh:mm:ss" format:')
                date_time = parser.parse(input())
            
            # Update the date time field in the EXIF and save
            image_exif[int(ExifTags.Base.DateTime)] = date_time.strftime("%Y:%m:%d %H:%M:%S")
            image.save(image_path, exif=image_exif)


if __name__ == "__main__":
    folder = "/Users/kevin/Desktop/Photos Test"

    if not os.path.isdir(folder):
        print(f'{folder} does not exist')
        exit()

    clean_folder(folder)