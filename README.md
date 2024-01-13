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
