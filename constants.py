import argparse

ns = {'sforce': 'http://soap.sforce.com/2006/04/metadata'}
XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'

# supported metadata
ELEMENT_TAGS = {
  "labels": "CustomLabels",
  "workflow": "Workflow",
  "profile": "Profile",
  "permissionset": "PermissionSet"
}

# name tags to name the element
# update when adding new supported metadata above
# ensure fullName is first for workflows. all other names are for profiles and permission sets
NAME_TAGS = ['fullName', 'application', 'apexClass', 'name', 'externalDataSource', 'flow',
            'object', 'apexPage', 'recordType', 'tab', 'field', 'startAddress',
            'dataCategoryGroup', 'layout', 'weekdayStart', 'friendlyname']

def parse_args():
    """Function to parse command line arguments."""
    parser = argparse.ArgumentParser(description='A script to de-compose Salesforce metadata.')
    parser.add_argument('-t', '--metadata-type', required=True,
                        choices=['labels', 'permissionset', 'workflow', 'profile'],
                        help='Specify the metadata type (labels, permissionset, workflow, profile)')
    parser.add_argument('-o', '--output', default='force-app/main/default',
                        help='Output directory for de-composed metadata files')
    args = parser.parse_args()
    return args
