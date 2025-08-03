import os
import re
from configparser import ConfigParser
from docx import Document
import gradio as gr

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
    parser.optionxform = str  # Preserve case
    parser['PLACEHOLDERS'] = {key: '' for key in placeholders}
    with open(filepath, 'w') as configfile:
        parser.write(configfile)

def replace_placeholders_in_doc(doc, props):
    for para in doc.paragraphs:
        for key, val in props.items():
            if f'{{{{{key}}}}}' in para.text:
                para.text = para.text.replace(f'{{{{{key}}}}}', val)
    return doc


def save_properties_and_generate_contract(values_dict):
    config = ConfigParser()
    config.optionxform = str  # Preserve case
    config["PLACEHOLDERS"] = values_dict
    with open(PROPERTIES_FILE, "w", encoding="utf-8") as f:
        config.write(f)

    doc = Document(TEMPLATE_FILE)  # Reload to avoid stale data
    doc = replace_placeholders_in_doc(doc, values_dict)
    doc.save(OUTPUT_FILE)
    return f"Rental contract generated in '{OUTPUT_FILE}'."



def main():
    if not os.path.exists(TEMPLATE_FILE):
        print(f"Template file '{TEMPLATE_FILE}' not found.")
        return

    doc = Document(TEMPLATE_FILE)
    placeholders = extract_placeholders_from_doc(doc)

    if not placeholders:
        print(f"No placeholders found in '{TEMPLATE_FILE}'.")
        return
    else:
        print(f"Launching Gradio UI with placeholders found: {placeholders}")
        
        # Gradio UI
        def launch_form(*input_values):
            values_dict = dict(zip(sorted_placeholders, input_values))
            return save_properties_and_generate_contract(values_dict)

        sorted_placeholders = sorted(placeholders)  # consistent field order
        inputs = [gr.Textbox(label=key) for key in sorted_placeholders]

        iface = gr.Interface(
            fn=launch_form,
            inputs=inputs,
            outputs="text",
            title="Fill Rental Contract Details",
            allow_flagging="never"
        )
        iface.launch(share=False, inbrowser=True)


if __name__ == '__main__':
    main()