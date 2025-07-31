import os
import re
from configparser import ConfigParser
from docx import Document

TEMPLATE_FILE = 'rental_template.docx'
PROPERTIES_FILE = 'rental.properties'
OUTPUT_FILE = 'generated_rental_contract.docx'

def extract_placeholders_from_doc(doc):
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return set(re.findall(r'\{\{(\w+)\}\}', text))

def read_properties(filepath):
    parser = ConfigParser()
    parser.optionxform = str  # Preserve case
    if os.path.exists(filepath):
        parser.read(filepath)
        return parser
    return None

def write_placeholder_properties(placeholders, filepath):
    parser = ConfigParser()
    parser['RENTAL'] = {key: '' for key in placeholders}
    parser['RENTAL']['generate'] = 'false'
    with open(filepath, 'w') as configfile:
        parser.write(configfile)

def replace_placeholders_in_doc(doc, props):
    for para in doc.paragraphs:
        for key, val in props.items():
            if f'{{{{{key}}}}}' in para.text:
                para.text = para.text.replace(f'{{{{{key}}}}}', val)
    return doc

def main():
    if not os.path.exists(TEMPLATE_FILE):
        print(f"Template file '{TEMPLATE_FILE}' not found.")
        return

    doc = Document(TEMPLATE_FILE)
    placeholders = extract_placeholders_from_doc(doc)

    config = read_properties(PROPERTIES_FILE)

    if config is None or 'RENTAL' not in config:
        print(f"Creating placeholder '{PROPERTIES_FILE}' with keys: {placeholders}")
        write_placeholder_properties(placeholders, PROPERTIES_FILE)
        input(f"\nPlease fill out '{PROPERTIES_FILE}' under [RENTAL], then press Enter to continue...")
        config = read_properties(PROPERTIES_FILE)

    if config:
        data = dict(config['RENTAL'])
        data.pop('generate', None)
        doc = Document(TEMPLATE_FILE)  # Reload to avoid stale data
        doc = replace_placeholders_in_doc(doc, data)
        doc.save(OUTPUT_FILE)
        print(f"Rental contract generated in '{OUTPUT_FILE}'.")
    else:
        print(f"Configuration not found in '{PROPERTIES_FILE}'. Exiting.")

if __name__ == '__main__':
    main()