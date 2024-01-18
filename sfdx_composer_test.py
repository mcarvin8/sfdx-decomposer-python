import hashlib
import json
import os
import sys

import sfdx_composer

FORCE_APP_DIR = 'force-app/main/default'
BASELINE_DIR = 'baselines'

def calculate_sha256(file_path):
    """Calculate the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def verify_hashes(baseline_directory, composed_directory):
    """Verify SHA-256 hashes of the composed files against the baseline directory."""
    # Dictionary to store hashes and corresponding relative file names
    hash_dict = {}
    # Iterate through files in baseline_directory
    for root, _, files in os.walk(baseline_directory):
        for file in files:
            file_path = os.path.join(root, file)
            hash_value = calculate_sha256(file_path)
            hash_dict[file] = hash_value

    # Check hashes in composed_directory
    for root, _, files in os.walk(composed_directory):
        for file in files:
            file_path = os.path.join(root, file)
            # Check if the file name exists in the baseline_directory hash_dict
            if file in hash_dict:
                hash_value = calculate_sha256(file_path)
                # Check if the hash matches
                if hash_value == hash_dict[file]:
                    print(f'Hash match for file {file}')
                    del hash_dict[file]

    # Print hash mismatches for files that have no match in BASELINE_DIR
    for file, hash_value in hash_dict.items():
        print(f'Hash mismatch: File {file} in {baseline_directory} has no match in {composed_directory}')

    # Check if all files in BASELINE_DIR have matches in FORCE_APP_DIR
    if not hash_dict:
        print(f'Success: All files in {baseline_directory} have matches in {composed_directory}.')
    else:
        print(f'ERROR: Not all files in {baseline_directory} have matches in {composed_directory}.')
        sys.exit(1)

# Load JSON file to get supported metadata
with open(os.path.abspath('metadata.json'), encoding='utf-8') as json_file:
    SUPPORTED_METADATA = json.load(json_file)

# Run the composer on each supported metadata type
for metadata_info in SUPPORTED_METADATA:
    metadata_type = metadata_info["metaSuffix"]
    sfdx_composer.main(metadata_type, FORCE_APP_DIR)

# Verify hashes
verify_hashes(BASELINE_DIR, FORCE_APP_DIR)
