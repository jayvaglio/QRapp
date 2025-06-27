
import streamlit as st
import qrcode
import segno
import uuid
import json
import zlib
import base64
import io
import datetime
from PIL import Image

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Helper: Generate structured data with a unique code
def generate_data():
    unique_code = f"PRD-{uuid.uuid4().hex[:12].upper()}"
    return {
        "code": unique_code,
        "created": datetime.datetime.utcnow().isoformat() + 'Z',
        "batch": "B42",
        "location": "KCMO",
        "version": "1.0",
        "status": "active"
    }, unique_code

# Helper: Compress and encode structured data
def compress_data(data_dict):
    json_str = json.dumps(data_dict)
    compressed = zlib.compress(json_str.encode())
    return base64.urlsafe_b64encode(compressed).decode()

# Helper: Generate QR code as Image object
def generate_qr_image(url):
    qr = qrcode.make(url)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)
    return Image.open(buf)

# Helper: Generate Data Matrix as Image object
def generate_dm_image(url):
    dm = segno.make(url, micro=False)
    buf = io.BytesIO()
    dm.save(buf, kind='png', scale=5)
    buf.seek(0)
    return Image.open(buf)

# Streamlit app layout
st.set_page_config(page_title="Barcode Generator Web App")
st.title("🔐 QR & Data Matrix Code Generator")

tabs = st.tabs(["🔄 Generate", "📜 History"])

with tabs[0]:
    if st.button("Generate New Code"):
        data, unique_code = generate_data()
        encoded_data = compress_data(data)
        url = f"https://www.enjoyablyengaging.com/{unique_code}"

        qr_image = generate_qr_image(url)
        dm_image = generate_dm_image(url)

        st.session_state.history.append({
            "url": url,
            "data": data,
            "qr_image": qr_image.copy()
        })

        st.subheader("Structured Data")
        st.json(data)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("QR Code")
            st.image(qr_image, caption=url, use_column_width=True)

        with col2:
            st.subheader("Data Matrix")
            st.image(dm_image, caption=url, use_column_width=True)

        st.success(f"URL: {url}")
    else:
        st.info("Click the button above to generate your first barcode.")

with tabs[1]:
    st.subheader("📜 Historical Log")
    if st.session_state.history:
        for i, entry in enumerate(reversed(st.session_state.history)):
            st.markdown(f"**{i+1}.** [{entry['url']}]({entry['url']})")
            st.json(entry['data'])
            st.image(entry['qr_image'], caption=entry['url'], use_column_width=False)
            st.markdown("---")
    else:
        st.info("No historical barcodes yet.")
