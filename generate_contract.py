import configparser

def read_properties(filename):
    """Reads a .properties file into a dictionary"""
    config = configparser.ConfigParser()
    with open(filename, 'r', encoding='utf-8') as f:
        # ConfigParser requires a section header, so we add a dummy one
        file_content = f"[DEFAULT]\n{f.read()}"
    config.read_string(file_content)
    return dict(config['DEFAULT'])

def replace_placeholders(template, values):
    """Replaces {{placeholder}} in the template with actual values"""
    for key, val in values.items():
        placeholder = f"{{{{{key}}}}}"
        template = template.replace(placeholder, val)
    return template

def main():
    # Read the properties
    props = read_properties('rental.properties')

    # Read the template
    with open('contract_template.txt', 'r', encoding='utf-8') as f:
        template = f.read()

    # Replace placeholders
    filled_template = replace_placeholders(template, props)

    # Write to output
    with open('rental_contract_output.txt', 'w', encoding='utf-8') as f:
        f.write(filled_template)

    print("Rental contract generated successfully.")

if __name__ == '__main__':
    main()