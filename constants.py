import argparse
import json
import os

ns = {'sforce': 'http://soap.sforce.com/2006/04/metadata'}
XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'

# Load JSON file to get supported metadata
with open(os.path.abspath('metadata.json'), encoding='utf-8') as json_file:
    SUPPORTED_METADATA = json.load(json_file)

def parse_args():
    """Function to parse command line arguments."""
    parser = argparse.ArgumentParser(description='A script to de-compose Salesforce metadata.')
    metadata_choices = [metadata["metaSuffix"] for metadata in SUPPORTED_METADATA]
    parser.add_argument('-t', '--metadata-type', required=True,
                        choices=metadata_choices,
                        help='Specify a supported metadata type')
    parser.add_argument('-o', '--output', default='force-app/main/default',
                        help='Output directory for de-composed metadata files')
    args = parser.parse_args()
    return args
