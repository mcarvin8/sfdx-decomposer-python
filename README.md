# SFDX Decomposer

Python scripts to decompose Salesforce metadata files into separate files for version control and recompose files compatible for deployments.

The following metadata types are supported:
- Custom Labels (`-t "labels"`)
- Workflows (`-t "workflow"`)
- Profiles (`-t "profile"`)
- Permission Sets (`-t "permissionset"`)
- Flows (`-t "flow"`)
- Matching Rules (`-t "matchingRule"`)
- Assignment Rules (`-t "assignmentRules"`)
- Escalation Rules (`-t "escalationRules"`)
- Sharing Rules (`-t "sharingRules"`)
- Auto Response Rules (`-t "autoResponseRules"`)

To decompose the original meta files, run the decomposer script for each metadata type after retrieving all metadata from your production org.

```
- python3 ./sfdx_decomposer.py -t "TYPE"
```

NOTE: This script will have issues for file-paths which exceed the operating system limit. Ensure you use short file-names when possible.

To recompose the files into meta files accepted for deployments, run the composer script for each metadata type:

```
- python3 ./sfdx_composer.py -t "TYPE"
```

By default, both scripts set the `-o`/`--output` argument to `force-app/main/default`. Supply this argument if your metadata is located in a different directory.

The `.gitignore` and `.forceignore` have been updated to have Git ignore the original meta files and have the Salesforce CLI ignore the decomposed meta files.

## Adding Metadata Types

To add a metadata type via a Pull Request:

1. Reference the metadata type details in https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_intro.htm
2. Add the metadata to the SUPPORTED_METADATA json in `constants.py`:
    - `directoryName` should be the root folder for that metadata type
    - `metaSuffix` should be the suffix the original meta files use (ex: `labels` is the suffix for `CustomLabels.labels-meta.xml`)
    - `xmlElement` should be the root element of the original meta files (ex: `CustomLabels` is the root element in meta header `<CustomLabels xmlns="http://soap.sforce.com/2006/04/metadata">`)
``` python
SUPPORTED_METADATA = [
    {
      "directoryName": "labels",
      "metaSuffix": "labels",
      "xmlElement": "CustomLabels"
    }
```
3. Using the Metadata API Developer Guide, ensure FIELD_NAMES in the `constants.py` contains the required field names for nested elements under the metadata type
    - In the below XML file, the `masterLabel` field name is a required field name for the nested valueTranslation element and should be  
``` xml
<?xml version="1.0" encoding="UTF-8"?>
<GlobalValueSetTranslation xmlns="http://soap.sforce.com/2006/04/metadata">
    <valueTranslation>
        <masterLabel>Three</masterLabel>
        <translation>Trois</translation>
    </valueTranslation>
    <valueTranslation>
        <masterLabel>Four</masterLabel>
        <translation>Quatre</translation>
    </valueTranslation>
    <valueTranslation>
        <masterLabel>Five</masterLabel>
        <translation><!-- Five --></translation>
    </valueTranslation>
</GlobalValueSetTranslation>
```

``` python
# field names used to name decomposed files for nested elements
# field names should be required per the Metadata API developer guide
# field names will be processed in the order they appear below
# ensure fullName is first since that is a default field from the Metadata type
FIELD_NAMES = ['fullName', 'application', 'apexClass', 'name', 'externalDataSource', 'flow',
            'object', 'apexPage', 'recordType', 'tab', 'field', 'startAddress',
            'dataCategoryGroup', 'layout', 'weekdayStart', 'friendlyname',
            'actionName', 'targetReference', 'assignToReference',
            'choiceText', 'promptText', 'masterLabel']
```