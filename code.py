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
    fill_color = request.json.get('fill_color', 'black')
    back_color = request.json.get('back_color', 'white')
    box_size = request.json.get('box_size', 10)

    if not data:
        return jsonify({"error": "Missing 'data' in request."}), 400

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)
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

# Color selection
st.write("Select QR Code colors:")
fill_color = st.color_picker("Pick a fill color", "#000000")
back_color = st.color_picker("Pick a background color", "#FFFFFF")

# QR code size selection
st.write("Select QR Code size:")
box_size = st.slider("Box Size", min_value=1, max_value=20, value=10)

# Text below QR code
text_below = st.text_input("Text Below QR Code", "")

def generate_qr_streamlit(data, fill_color, back_color, box_size, text_below):
    """Sends the data to the Flask API and fetches the QR code."""
    if not data:
        st.error("Please provide input data.")
        return

    try:
        response = requests.post("http://127.0.0.1:5000/generate_qr", 
                                 json={"data": data, "fill_color": fill_color, "back_color": back_color, "box_size": box_size})
        if response.status_code == 200:
            qr_image = Image.open(BytesIO(response.content))
            st.image(qr_image, caption="Generated QR Code")

            # Display text below QR code if provided
            if text_below:
                st.write(f"**{text_below}**")

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
    generate_qr_streamlit(user_input, fill_color, back_color, box_size, text_below)
