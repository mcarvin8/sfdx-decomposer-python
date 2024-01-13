# SFDX Decomposer

Python scripts to decompose Salesforce metadata files into separate files for version control and recompose files compatible for deployments.

The following metadata types are supported:
- Custom Labels
- Workflows
- Profiles
- Permission Sets
- Flows

To decompose the original meta files, run the decomposer script for each metadata type after retrieving all metadata from your production org.

```
- python3 ./sfdx_decomposer.py -t "labels"
- python3 ./sfdx_decomposer.py -t "permissionset"
- python3 ./sfdx_decomposer.py -t "workflow"
- python3 ./sfdx_decomposer.py -t "profile"
- python3 ./sfdx_decomposer.py -t "flow"
```

NOTE: This script will have issues for file-paths which exceed the operating system limit. Ensure you use short file-names when possible.

To recompose the files into meta files accepted for deployments, run the composer script for each metadata type:

```
- python3 ./sfdx_composer.py -t "labels"
- python3 ./sfdx_composer.py -t "permissionset"
- python3 ./sfdx_composer.py -t "workflow"
- python3 ./sfdx_composer.py -t "profile"
- python3 ./sfdx_composer.py -t "flow"
```

By default, both scripts set the `-o`/`--output` argument to `force-app/main/default`. Supply this argument if your metadata is located in a different directory.

The `.gitignore` and `.forceignore` have been updated to have Git ignore the original meta files and have the Salesforce CLI ignore the decomposed meta files.
