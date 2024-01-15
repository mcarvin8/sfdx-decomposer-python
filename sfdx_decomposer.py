import logging
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

from constants import XML_HEADER, ns, SUPPORTED_METADATA, parse_args

logging.basicConfig(format='%(message)s', level=logging.DEBUG)

def extract_field_name(element, namespace, field_names):
    """Extract the field name from a nested element."""
    field_name = None
    for field_name in field_names:
        # update to find nested elements
        field_name = element.find(f'.//sforce:{field_name}', namespace)
        if field_name is not None:
            break  # Break the loop if a matching field name is found

    return field_name.text if field_name is not None else None

def format_xml_contents(xml_contents):
    """Format XML before writing it."""
    # Remove extra new lines
    formatted_xml = '\n'.join(line for line in xml_contents.split('\n') if line.strip())

    # Remove existing XML declaration
    formatted_xml = '\n'.join(line for line in formatted_xml.split('\n') if not line.strip().startswith('<?xml'))
    return formatted_xml

def create_meta_xml_file(contents, file_name):
    """Create a new XML file with un-nested meta elements."""
    root = contents.getroot()
    sorted_elements = sorted(root, key=lambda elem: (elem.tag.split('}')[-1], elem.text))

    # Create a new XML tree with sorted elements
    sorted_tree = ET.ElementTree(ET.Element(root.tag, attrib=root.attrib))
    sorted_root = sorted_tree.getroot()
    sorted_root.extend(sorted_elements)

    unformatted_xml = minidom.parseString(ET.tostring(sorted_root)).toprettyxml(indent="    ")
    formatted_xml = format_xml_contents(unformatted_xml)

    with open(file_name, 'wb') as file:
        file.write(XML_HEADER.encode('utf-8'))
        file.write(formatted_xml.encode('utf-8'))
    logging.info('Saved meta content to %s', file_name)

def create_nested_xml_file(label, parent_directory, tag, field_name, parent_metadata_name=None):
    """Create a new XML file with nested elements."""
    tag_without_namespace = tag.split('}')[-1] if '}' in tag else tag

    if parent_metadata_name:
        subfolder = os.path.join(parent_directory, parent_metadata_name, tag_without_namespace)
    else:
        subfolder = os.path.join(parent_directory)

    os.makedirs(subfolder, exist_ok=True)  # Ensure the subfolder exists

    # ensure file extension for labels is unique from the original meta file
    if tag_without_namespace == 'labels':
        tag_without_namespace = tag_without_namespace.replace('s','')

    output_filename = f'{subfolder}/{field_name}.{tag_without_namespace}-meta.xml'

    # Remove the namespace prefix from the element tags
    for element in label.iter():
        if '}' in element.tag:
            element.tag = element.tag.split('}')[1]

    xml_content = ET.tostring(label, encoding='utf-8').decode('utf-8')
    dom = minidom.parseString(xml_content)
    unformatted_xml = dom.toprettyxml(indent='    ')

    formatted_xml = format_xml_contents(unformatted_xml)

    with open(output_filename, 'wb') as file:
        file.write(XML_HEADER.encode('utf-8'))
        file.write(formatted_xml.encode('utf-8'))

    logging.info('Saved %s element content to %s', tag, output_filename)

def parse_xml_file(metadata_file_path):
    """Parse the XML file and return the root.."""
    try:
        tree = ET.parse(metadata_file_path)
        root = tree.getroot()
        return root
    except FileNotFoundError:
        logging.info("Error: XML file '%s' not found.", metadata_file_path)
    except ET.ParseError:
        logging.info("Error: Unable to parse the XML file.")
    return None

def create_single_elements(xml_root_element):
    """"Create an element for un-nested elements."""
    return ET.Element(xml_root_element)

def process_metadata_file(metadata_directory, filename, metadata_type, expected_extension, xml_root_element, field_names):
    """Process a single metadata file and extract elements."""
    metadata_file_path = os.path.join(metadata_directory, filename)
    root = parse_xml_file(metadata_file_path)

    # Extract all unique XML tags dynamically
    xml_tags = {elem.tag for elem in root.iter() if '}' in elem.tag}

    # Extract the parent metadata name from the XML file name if not labels
    if metadata_type != 'labels':
        parent_metadata_name = filename.split('.')[0]
    else:
        parent_metadata_name = None

    single_elements = create_single_elements(xml_root_element)

    # Iterate through the dynamically extracted XML tags
    for tag in xml_tags:
        for _, label in enumerate(root.findall(tag, ns)):
            # determine if single element or nested element
            if not label.text.isspace():
                # Append single elements to the root
                single_element = ET.Element(label.tag.split('}')[1])
                single_element.text = label.text
                single_elements.append(single_element)
            else:
                field_name = extract_field_name(label, ns, field_names)
                if field_name:
                    create_nested_xml_file(label, metadata_directory, tag,
                                           field_name, parent_metadata_name)
                else:
                    logging.info('Skipping %s element without a supported field name', tag)

    # only create an XML with un-nested elements if there are any
    if len(list(single_elements.iter())) > 1:
        single_tree = ET.ElementTree(single_elements)
        create_meta_xml_file(single_tree,
                             os.path.join(metadata_directory,
                             parent_metadata_name,
                             f'{parent_metadata_name}{expected_extension}'))

def process_directory(metadata_directory, metadata_type, meta_extension, xml_root_element, field_names):
    """Recursively process metadata files in the directory and its subdirectories."""
    for root, _, files in os.walk(metadata_directory):
        for filename in files:
            if filename.endswith(meta_extension):
                process_metadata_file(root, filename, metadata_type,
                                      meta_extension, xml_root_element, field_names)

def separate_metadata(metadata_directory, metadata_type, meta_extension, xml_root_element, field_names, recurse=False):
    """Separate metadata into individual XML files."""
    expected_extension = f".{meta_extension}-meta.xml"
    if recurse:
        process_directory(metadata_directory, metadata_type, expected_extension, xml_root_element, field_names)
    else:
        # Process files only in the specified directory without recursion
        for filename in os.listdir(metadata_directory):
            if filename.endswith(expected_extension):
                process_metadata_file(metadata_directory, filename, metadata_type, expected_extension, xml_root_element, field_names)

def main(metadata_type, output_directory):
    """Main function."""
    metadata_folder = None
    for metadata_info in SUPPORTED_METADATA:
        if metadata_info["metaSuffix"] == metadata_type:
            metadata_folder = metadata_info["directoryName"]
            meta_extension = metadata_info["metaSuffix"]
            xml_root_element = metadata_info["xmlElement"]
            field_names = metadata_info["fieldNames"].split(',')
            recurse = metadata_info.get("recurse", None)
            break

    if not metadata_folder:
        return

    metadata_directory = os.path.join(output_directory, metadata_folder)
    separate_metadata(metadata_directory, metadata_type,
                      meta_extension, xml_root_element, field_names,
                      recurse)

if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.metadata_type, inputs.output)