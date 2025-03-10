import streamlit as st
import requests
import os
from fpdf import FPDF
from docx import Document

# Get the API key from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")
API_KEY = st.secrets["api_keys"]["GEMINI_API_KEY"]

# Check if the API key is loaded
if not API_KEY:
    st.error("API key is missing. Please set the GEMINI_API_KEY environment variable.")
    st.stop()  # Prevent the rest of the code from running
else:
    st.write(f"API Key Loaded: {API_KEY[:10]}...")  # Print part of the key for verification

# Set up the app title
st.title("AI Recommendation Letter Generator")

# Input fields for user details
user_details = st.text_area("Enter user details:")
application_purpose = st.text_input("Application Purpose", "a STEM opportunity")
template_choice = st.selectbox("Template Style", ["default", "technical", "analytical"])
export_format = st.radio("Export Format", ["Text", "PDF", "Word"])

# Button to trigger letter generation
if st.button("Generate Letter"):
    # Prepare the API request payload
    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"Generate a recommendation letter for a {application_purpose} application. "
                             f"User details: {user_details}. Template style: {template_choice}."}
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    # Use the correct Gemini API URL
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    try:
        # Send the POST request to generate the letter
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()  # Check for any errors
        
        # Extract only the letter content
        response_json = response.json()
        letter_content = response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No letter content returned.")

        # Display the generated letter in the app
        st.text_area("Generated Letter", letter_content, height=300)

        # Export the generated letter to PDF or Word based on user selection
        if export_format == "PDF":
            pdf = FPDF()
            pdf.add_page()

            # Set font to a basic font that supports Unicode characters
            pdf.set_font("Arial", size=12)

            # Ensure proper encoding for special characters
            letter_content_encoded = letter_content.encode('latin-1', 'replace').decode('latin-1')

            # Add the content to the PDF
            pdf.multi_cell(0, 10, letter_content_encoded)
            
            # Save the PDF
            pdf_filename = "recommendation_letter.pdf"
            pdf.output(pdf_filename)

            # Allow the user to download the PDF
            with open(pdf_filename, "rb") as file:
                st.download_button("Download PDF", file, file_name=pdf_filename, mime="application/pdf")

        elif export_format == "Word":
            doc = Document()
            doc.add_paragraph(letter_content)
            word_filename = "recommendation_letter.docx"
            doc.save(word_filename)
            with open(word_filename, "rb") as file:
                st.download_button("Download Word", file, file_name=word_filename, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    except requests.exceptions.RequestException as e:
        # Show an error message if the API request fails
        st.error(f"Error generating letter: {e}")
