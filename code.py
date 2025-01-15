from flask import Flask, request, jsonify, send_file
import qrcode
from io import BytesIO
import threading
import requests
import streamlit as st
from PIL import Image

# Flask Application
app = Flask(__name__)

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.json.get('data')
    if not data:
        return jsonify({"error": "Missing 'data' in request."}), 400

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png", as_attachment=True, download_name="qrcode.png")

def run_flask():
    """Run the Flask app in a separate thread."""
    app.run(debug=False, use_reloader=False)

# Start Flask server in a thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Streamlit Application
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
            
            # Download functionality
            buffer = BytesIO(response.content)
            st.download_button(
                label="Download QR Code",
                data=buffer,
                file_name="qrcode.png",
                mime="image/png"
            )
            
            st.success("QR Code generated successfully!")
        else:
            st.error("Failed to generate QR code. " + response.text)
    except Exception as e:
        st.error(f"Error: {e}")

if st.button("Generate QR Code"):
    generate_qr_streamlit(user_input)
