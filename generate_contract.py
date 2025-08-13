import streamlit as st
import re
from docx import Document
from io import BytesIO

def extract_placeholders(docx_file):
    doc = Document(docx_file)
    text = "\n".join([p.text for p in doc.paragraphs])
    return sorted(re.findall(r"\{\{(.*?)\}\}", text))

def fill_template(docx_file, values):
    doc = Document(docx_file)
    for p in doc.paragraphs:
        for placeholder, value in values.items():
            p.text = p.text.replace(f"{{{{{placeholder}}}}}", value)
    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output

st.title("Contract Generator")

uploaded_file = st.file_uploader("Upload Template (.docx)", type="docx")
if uploaded_file:
    placeholders = {s for s in extract_placeholders(uploaded_file)}
    user_values = {}
    for ph in placeholders:
        user_values[ph] = st.text_input(f"{ph}")

    if st.button("Generate Contract"):
        filled_template = fill_template(uploaded_file, user_values)
        st.download_button(
            "Download Contract",
            data=filled_template,
            file_name="contract_filled.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )