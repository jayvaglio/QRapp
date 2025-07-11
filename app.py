import streamlit as st
import qrcode
import segno
import uuid
import json
import zlib
import base64
import io
import datetime
import hashlib
from PIL import Image

# Blockchain classes
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        record = f'{self.index}{self.timestamp}{self.data}{self.previous_hash}'
        return hashlib.sha256(record.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        genesis_data = {"message": "Genesis Block"}
        return Block(0, datetime.datetime.utcnow().isoformat(), json.dumps(genesis_data), '0')

    def latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        new_block = Block(len(self.chain), datetime.datetime.utcnow().isoformat(), data, self.latest_block().hash)
        self.chain.append(new_block)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'ledger' not in st.session_state:
    st.session_state.ledger = Blockchain()
if 'scan_counts' not in st.session_state:
    st.session_state.scan_counts = {}
if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        "location": "KCMO",
        "datetime": datetime.datetime.utcnow().isoformat(),
        "sponsors": []
    }

# Helper functions
def generate_data(form_data):
    unique_code = f"PRD-{uuid.uuid4().hex[:12].upper()}"
    return {
        "code": unique_code,
        "created": datetime.datetime.utcnow().isoformat() + 'Z',
        "batch": "B42",
        "location": form_data['location'],
        "datetime": form_data['datetime'],
        "sponsors": form_data['sponsors'],
        "version": "1.0",
        "status": "active"
    }, unique_code

def compress_data(data_dict):
    json_str = json.dumps(data_dict)
    compressed = zlib.compress(json_str.encode())
    return base64.urlsafe_b64encode(compressed).decode()

def generate_qr_image(url):
    qr = qrcode.make(url)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)
    return Image.open(buf)

def generate_dm_image(url):
    dm = segno.make(url, micro=False)
    buf = io.BytesIO()
    dm.save(buf, kind='png', scale=5)
    buf.seek(0)
    return Image.open(buf)

# App Layout
st.set_page_config(page_title="Barcode Generator with Blockchain")
st.title("🔐 QR & Data Matrix Generator with Ledger")

# Overview stats
total_codes = len(st.session_state.history)
total_scans = sum(st.session_state.scan_counts.values())
st.markdown(f"📊 **Overview:** `{total_codes}` codes generated | `{total_scans}` total scans")

# Tabs
tabs = st.tabs(["📝 Criteria", "🔄 Generate", "📜 History", "⛓ Ledger"])

# Tab 1: Criteria input
with tabs[0]:
    st.subheader("Enter QR Code Generation Criteria")
    st.session_state.form_data['location'] = st.text_input("📍 Location", st.session_state.form_data['location'])
    st.session_state.form_data['datetime'] = st.text_input("🕒 DateTime (ISO format)", st.session_state.form_data['datetime'])
    sponsors_input = st.text_area("🤝 Sponsors (comma-separated)", value=",".join(st.session_state.form_data['sponsors']))
    st.session_state.form_data['sponsors'] = [s.strip() for s in sponsors_input.split(",") if s.strip()]

# Tab 2: Generate
with tabs[1]:
    if st.button("Generate New Code"):
        data, unique_code = generate_data(st.session_state.form_data)
        encoded_data = compress_data(data)
        url = f"https://www.enjoyablyengaging.com/{unique_code}"

        qr_image = generate_qr_image(url)
        dm_image = generate_dm_image(url)

        st.session_state.history.append({
            "url": url,
            "data": data,
            "qr_image": qr_image.copy()
        })

        st.session_state.ledger.add_block(json.dumps(data))
        st.session_state.scan_counts[url] = 0  # Simulated scan counter

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

# Tab 3: History
with tabs[2]:
    st.subheader("📜 Historical Log")
    if st.session_state.history:
        for i, entry in enumerate(reversed(st.session_state.history)):
            count = st.session_state.scan_counts.get(entry['url'], 0)
            st.markdown(f"**{i+1}.** [{entry['url']}]({entry['url']}) — 📈 Scans: `{count}`")
            st.json(entry['data'])
            st.image(entry['qr_image'], caption=entry['url'], use_column_width=False)
            st.markdown("---")
    else:
        st.info("No historical barcodes yet.")

# Tab 4: Blockchain Ledger
with tabs[3]:
    st.subheader("⛓ Blockchain Ledger")
    for block in st.session_state.ledger.chain:
        st.write(f"Block {block.index} | Hash: {block.hash[:12]}... | Prev: {block.previous_hash[:12]}...")
        try:
            st.json(json.loads(block.data))
        except:
            st.write(block.data)
        st.markdown("---")
