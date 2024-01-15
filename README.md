# SFDX Decomposer

Python scripts to decompose Salesforce metadata files into separate files for version control and recompose files compatible for deployments.

## Supported Metadata
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
- Global Value Set Translation (`-t "globalValueSetTranslation"`)
- Standard Value Set Translation (`-t "standardValueSetTranslation"`)
- Marketing App Extension (`-t "marketingappextension"`)

**NOTE**:
Per Salesforce documentation for **Translations**, when a value isn't translated, its translation becomes a comment that's paired with its label. 
``` xml
    <valueTranslation>
        <masterLabel>Warm</masterLabel>
        <translation><!-- Warm --></translation>
    </valueTranslation>
```
The decompose script will not process these comments correctly. Ensure all translation meta files have proper translations before decomposing them.

## Decompose Files
To decompose the original meta files, run the decomposer script for each metadata type after retrieving all metadata from your production org.

```
- python3 ./sfdx_decomposer.py -t "TYPE"
```
Arguments:
- `-t`/`--metadata-type` - metadata type to process (same value as the `metaSuffix` value in `constants.py`)
- `-o`/`--output` - directory containing the metadata (defaults to `force-app/main/default` if the argument isn't provided)
NOTE: This script will have issues for file-paths which exceed the operating system limit. Ensure you use short file-names when possible.

## Compose Files
To recompose the files into meta files accepted for deployments, run the composer script for each metadata type:

```
- python3 ./sfdx_composer.py -t "TYPE"
```
Arguments:
- `-t`/`--metadata-type` - metadata type to process (same value as the `metaSuffix` value in `constants.py`)
- `-o`/`--output` - directory containing the metadata (defaults to `force-app/main/default` if the argument isn't provided)

## Ignore Files

The `.gitignore` and `.forceignore` have been updated to have Git ignore the original meta files and have the Salesforce CLI ignore the decomposed meta files.

Salesforce CLI version 2.10.2 correctly handles opt-in style with directories on the forceignore (https://github.com/forcedotcom/cli/issues/2404). Ensure you're using a version of the CLI which supports opt-in style with directories.

## Adding Metadata Types

To add a metadata type via a Pull Request:

1. Reference the metadata type details in https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_intro.htm
2. Add the metadata to `metadata.json`:
    - `directoryName` should be the root folder for that metadata type
    - `metaSuffix` should be the suffix the original meta files use (ex: `labels` is the suffix for `CustomLabels.labels-meta.xml`)
    - `xmlElement` should be the root element of the original meta files (ex: `CustomLabels` is the root element in meta header `<CustomLabels xmlns="http://soap.sforce.com/2006/04/metadata">`)
    - `fieldNames` should contain a comma-seperated list (no spaces) of Required Field Names for Nested Elements under the metadata type
        - In the below XML file, the `apexClass` field name is a required field name for the nested `<classAccesses>` element and should be included in possible field names for permission set
        - Fields which do not have nested elements such as `<description>` should not be included in `fieldNames` (All unnested elements will be added to the same meta file when decomposed)
        - Field Names will be evaluated in the order they appear in the list (ensure `fullName` is first since it's inherited from the Metadata type)
``` json
  {
    "directoryName": "permissionsets",
    "metaSuffix": "permissionset",
    "xmlElement": "PermissionSet",
    "fieldNames": "fullName,application,apexClass,name,externalDataSource,flow,object,apexPage,recordType,tab,field"
  },
```

``` xml
<?xml version="1.0" encoding="UTF-8"?>
<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Grants all rights needed for an HR administrator to manage employees.</description>
    <label>HR Administration</label>
    <userLicense>Salesforce</userLicense>
    <applicationVisibilities>
        <application>JobApps__Recruiting</application>
        <visible>true</visible>
    </applicationVisibilities>
    <userPermissions>
        <enabled>true</enabled>
        <name>APIEnabled</name>
    </userPermissions>
    <objectPermissions>
        <allowCreate>true</allowCreate>
        <allowDelete>true</allowDelete>
        <allowEdit>true</allowEdit>
        <allowRead>true</allowRead>
        <viewAllRecords>true</viewAllRecords>
        <modifyAllRecords>true</modifyAllRecords>
        <object>Job_Request__c</object>
    </objectPermissions>
    <fieldPermissions>
        <editable>true</editable>
        <field>Job_Request__c.Salary__c</field>
        <readable>true</readable>
    </fieldPermissions>
    <pageAccesses>
        <apexPage>Job_Request_Web_Form</apexPage>
        <enabled>true</enabled>
    </pageAccesses>
    <classAccesses>
      <apexClass>Send_Email_Confirmation</apexClass>
      <enabled>true</enabled>
    </classAccesses>
    <tabSettings>
        <tab>Job_Request__c</tab>
        <visibility>Available</visibility>
    </tabSettings>
    <recordTypeVisibilities>
        <recordType>Recruiting.DevManager</recordType>
        <visible>true</visible>
    </recordTypeVisibilities>
</PermissionSet>
```

4. Update the `.forceignore` to ignore the decomposed meta files and allow (`!`) the original meta files
5. Update the `.gitignore` to ignore the original meta files
6. Run the `sfdx_decomposer.py` script to decompose the original meta files for the new metadata type. Confirm the files are decomposed as intended.
7. Run the `sfdx_composer.py` script to recompose the meta files for the new metadata type. Confirm the meta files created are accepted for deployments.
