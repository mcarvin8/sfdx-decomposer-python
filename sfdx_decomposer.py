import logging
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

from constants import XML_HEADER, ns, ELEMENT_TAGS, NAME_TAGS, parse_args

logging.basicConfig(format='%(message)s', level=logging.DEBUG)

def extract_full_name(element, namespace):
    """Extract the full name from a given XML element."""
    full_name_element = None
    for tag in NAME_TAGS:
        # update to find nested elements
        full_name_element = element.find(f'.//sforce:{tag}', namespace)
        if full_name_element is not None:
            break  # Break the loop if a matching tag is found

    return full_name_element.text if full_name_element is not None else None

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

    try:
        with open(file_name, 'wb') as file:
            file.write(XML_HEADER.encode('utf-8'))
            file.write(formatted_xml.encode('utf-8'))
        logging.info('Saved meta content to %s', file_name)
    except Exception as e:
        logging.info('ERROR writing file: %s', file_name)
        logging.info('%s', e)

def create_nested_xml_file(label, parent_directory, tag, full_name, parent_metadata_name=None):
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

    output_filename = f'{subfolder}/{full_name}.{tag_without_namespace}-meta.xml'

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

def create_single_elements(metadata_type):
    """"Create an element for un-nested elements."""
    return ET.Element(ELEMENT_TAGS.get(metadata_type))

def process_metadata_file(metadata_directory, filename, metadata_type, expected_extension):
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

    single_elements = create_single_elements(metadata_type)

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
                full_name = extract_full_name(label, ns)
                if full_name:
                    create_nested_xml_file(label, metadata_directory, tag,
                                           full_name, parent_metadata_name)
                else:
                    logging.info('Skipping %s element without fullName', tag)

    # only create an XML with un-nested elements if there are any
    if len(list(single_elements.iter())) > 1:
        single_tree = ET.ElementTree(single_elements)
        create_meta_xml_file(single_tree,
                             os.path.join(metadata_directory,
                             parent_metadata_name,
                             f'{parent_metadata_name}{expected_extension}'))

def separate_metadata(metadata_directory, metadata_type):
    """Separate metadata into individual XML files."""
    # Iterate through the directory to process files
    for filename in os.listdir(metadata_directory):
        expected_extension = f".{metadata_type}-meta.xml"
        if filename.endswith(expected_extension):
            process_metadata_file(metadata_directory, filename, metadata_type, expected_extension)

def main(metadata_type, output_directory):
    """Main function."""
    if metadata_type != 'labels' and metadata_type != 'assignmentRules':
        metadata_folder = f"{metadata_type}s"
    else:
        metadata_folder = metadata_type
    metadata_directory = os.path.join(output_directory, metadata_folder)
    separate_metadata(metadata_directory, metadata_type)

if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.metadata_type, inputs.output)
