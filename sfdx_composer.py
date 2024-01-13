import logging
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

from constants import XML_HEADER, SUPPORTED_METADATA, parse_args

logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def read_individual_xmls(metadata_directory, expected_extension, metadata_type):
    """Read each XML file."""
    individual_xmls = {}

    def process_metadata_file(filepath, parent_metadata_type):
        tree = ET.parse(filepath)
        root = tree.getroot()
        individual_xmls.setdefault(parent_metadata_type, []).append(root)

    for root, _, files in os.walk(metadata_directory):
        for filename in files:
            if filename.endswith('.xml') and not filename.endswith(expected_extension):
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, metadata_directory)
                if metadata_type != 'labels':
                    parent_metadata_type = relative_path.split(os.path.sep)[0]
                else:
                    parent_metadata_type = 'CustomLabels'
                process_metadata_file(file_path, parent_metadata_type)

    # Sort by type and then alphabetically
    sorted_individual_xmls = {k: sorted(v, key=lambda x: x.tag) for k, v in sorted(individual_xmls.items())}

    return sorted_individual_xmls

def has_subelements(element):
    """Check if an XML element has sub-elements."""
    return any(element.iter())

def merge_xml_content(individual_xmls, xml_tag):
    """Merge XMLs for each object."""
    merged_xmls = {}
    for parent_metadata_type, individual_roots in individual_xmls.items():
        parent_metadata_root = ET.Element(xml_tag, xmlns="http://soap.sforce.com/2006/04/metadata")

        # Sort individual_roots by tag to match Salesforce CLI output
        individual_roots.sort(key=lambda x: x.tag)

        for matching_root in individual_roots:
            tag = matching_root.tag
            # Check if the root has sub-elements
            if has_subelements(matching_root):
                # Create a new XML element for each sub-element
                child_element = ET.Element(tag)
                parent_metadata_root.append(child_element)
                child_element.extend(matching_root)
            else:
                # Extract text content from single-element XML and append to the parent
                text_content = matching_root.text
                if text_content:
                    child_element = ET.Element(tag)
                    child_element.text = text_content
                    parent_metadata_root.append(child_element)

        merged_xmls[parent_metadata_type] = parent_metadata_root

    return merged_xmls

def format_and_write_xmls(merged_xmls, metadata_directory, expected_extension):
    """Create the final XMLs."""
    for parent_metadata_type, parent_metadata_root in merged_xmls.items():
        # Load the parent meta file if it exists in the sub-folder (profiles and perm sets)
        existing_meta_file_path = os.path.join(metadata_directory, parent_metadata_type, f'{parent_metadata_type}{expected_extension}')
        if os.path.exists(existing_meta_file_path):
            existing_tree = ET.parse(existing_meta_file_path)
            existing_root = existing_tree.getroot()

            # Iterate through the sub-elements in the existing meta file
            for existing_sub_element in existing_root:
                # Check if the sub-element is not already present in the merged XML
                if not any(existing_sub_element.tag == child.tag for child in parent_metadata_root):
                    parent_metadata_root.append(existing_sub_element)

        parent_xml_str = ET.tostring(parent_metadata_root, encoding='utf-8').decode('utf-8')
        formatted_xml = minidom.parseString(parent_xml_str).toprettyxml(indent="    ")

        # Remove extra new lines
        formatted_xml = '\n'.join(line for line in formatted_xml.split('\n') if line.strip())

        # Remove existing XML declaration
        formatted_xml = '\n'.join(line for line in formatted_xml.split('\n') if not line.strip().startswith('<?xml'))

        parent_metadata_filename = os.path.join(metadata_directory, f'{parent_metadata_type}{expected_extension}')
        with open(parent_metadata_filename, 'wb') as file:
            file.write(XML_HEADER.encode('utf-8'))
            file.write(formatted_xml.encode('utf-8'))

def combine_metadata(output_directory, metadata_type, meta_extension, xml_tag):
    """Combine the metadata for deployments."""
    expected_extension = f".{meta_extension}-meta.xml"
    individual_xmls = read_individual_xmls(output_directory, expected_extension, metadata_type)
    merged_xmls = merge_xml_content(individual_xmls, xml_tag)
    format_and_write_xmls(merged_xmls, output_directory, expected_extension)


    logging.info('The metadata type `%s` has been compiled for deployments.', metadata_type)

def main(metadata_type, output_directory):
    """Main function."""
    metadata_folder = None
    for metadata_info in SUPPORTED_METADATA:
        if metadata_info["metaTag"] == metadata_type:
            metadata_folder = metadata_info["directoryName"]
            meta_extension = metadata_info["metaTag"]
            xml_tag = metadata_info["xmlTag"]
            break
    metadata_directory = os.path.join(output_directory, metadata_folder)
    combine_metadata(metadata_directory, metadata_type,
                     meta_extension, xml_tag)

if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.metadata_type, inputs.output)
