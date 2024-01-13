import argparse

ns = {'sforce': 'http://soap.sforce.com/2006/04/metadata'}
XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'

# supported metadata
SUPPORTED_METADATA = [
    {
      "directoryName": "labels",
      "metaTag": "labels",
      "xmlTag": "CustomLabels"
    },
    {
      "directoryName": "workflows",
      "metaTag": "workflow",
      "xmlTag": "Workflow"
    },
    {
      "directoryName": "profiles",
      "metaTag": "profile",
      "xmlTag": "Profile"
    },
    {
      "directoryName": "permissionsets",
      "metaTag": "permissionset",
      "xmlTag": "PermissionSet"
    },
    {
      "directoryName": "matchingRules",
      "metaTag": "matchingRule",
      "xmlTag": "MatchingRules"
    },
    {
      "directoryName": "assignmentRules",
      "metaTag": "assignmentRules",
      "xmlTag": "AssignmentRules"
    },
    {
      "directoryName": "flows",
      "metaTag": "flow",
      "xmlTag": "Flow"
    }
]

# name tags to name the element
# update when adding new supported metadata above
# ensure fullName is first for workflows. all other names are for profiles and permission sets
NAME_TAGS = ['fullName', 'application', 'apexClass', 'name', 'externalDataSource', 'flow',
            'object', 'apexPage', 'recordType', 'tab', 'field', 'startAddress',
            'dataCategoryGroup', 'layout', 'weekdayStart', 'friendlyname',
            'actionName', 'targetReference', 'assignToReference',
            'choiceText', 'promptText']

def parse_args():
    """Function to parse command line arguments."""
    parser = argparse.ArgumentParser(description='A script to de-compose Salesforce metadata.')
    metadata_choices = [metadata["metaTag"] for metadata in SUPPORTED_METADATA]
    parser.add_argument('-t', '--metadata-type', required=True,
                        choices=metadata_choices,
                        help='Specify a supported metadata type')
    parser.add_argument('-o', '--output', default='force-app/main/default',
                        help='Output directory for de-composed metadata files')
    args = parser.parse_args()
    return args
