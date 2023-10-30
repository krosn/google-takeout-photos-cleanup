import os
import re
from collections import defaultdict

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

        # TODO: Default year for missing dates via prompt

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

def ensure_date_set(dir_name: str, files_to_keep: list[str]) -> None:
    pass


if __name__ == "__main__":
    folder = "/Users/kevin/Desktop/Photos Test"

    if not os.path.isdir(folder):
        print(f'{folder} does not exist')
        exit()

    clean_folder(folder)