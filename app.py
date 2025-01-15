import requests
import streamlit as st
from PIL import Image
from io import BytesIO

st.title("QR Code Generator")

st.write("Enter the text or URL to generate a QR code:")

# Input field for user data
user_input = st.text_input("Input Data", "")

def generate_qr_streamlit(data):
    """Sends the data to the Flask API and fetches the QR code."""
    if not data:
        st.error("Please provide input data.")
        return

    try:
        response = requests.post("http://127.0.0.1:5000/generate_qr", json={"data": data})
        if response.status_code == 200:
            qr_image = Image.open(BytesIO(response.content))
            st.image(qr_image, caption="Generated QR Code")
            st.success("QR Code generated successfully!")
        else:
            st.error("Failed to generate QR code. " + response.text)
    except Exception as e:
        st.error(f"Error: {e}")

if st.button("Generate QR Code"):
    generate_qr_streamlit(user_input)
