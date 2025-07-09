
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
        genesis_data = {"message": "Hello, World!"}
        return Block(0, datetime.datetime.utcnow().isoformat(), json.dumps(genesis_data), '0')

    def latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        new_block = Block(len(self.chain), datetime.datetime.utcnow().isoformat(), data, self.latest_block().hash)
        self.chain.append(new_block)

# Initialize state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'ledger' not in st.session_state:
    st.session_state.ledger = Blockchain()

# Helpers
def generate_data():
    unique_code = f"enjoy-{uuid.uuid4().hex[:12].upper()}"
    return {
        "code": unique_code,
        "created": datetime.datetime.utcnow().isoformat() + 'Z',
        "batch": "B42",
        "location": "KCMO",
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

# Layout
st.set_page_config(page_title="Event ID Generator")
st.title("🔐 Event ID Generator")

tabs = st.tabs(["🔄 Generate", "📜 History", "⛓ Ledger"])

with tabs[0]:
    if st.button("Generate Event ID"):
        data, unique_code = generate_data()
        url = f"https://www.enjoyablyengaging.com/{unique_code}"
        qr_image = generate_qr_image(url)
        dm_image = generate_dm_image(url)

        st.session_state.history.append({
            "url": url,
            "data": data,
            "qr_image": qr_image.copy()
        })

        st.session_state.ledger.add_block(json.dumps(data))

        st.subheader("Structured Data")
        st.json(data)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("QR Code")
            st.image(qr_image, caption=url, use_column_width=True)
        #with col2:
         #   st.subheader("Data Matrix")
          #  st.image(dm_image, caption=url, use_column_width=True)

        st.success(f"URL: {url}")

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

with tabs[2]:
    st.subheader("⛓ Blockchain Ledger")
    for block in st.session_state.ledger.chain:
        st.write(f"Block {block.index} | Hash: {block.hash[:12]}... | Prev: {block.previous_hash[:12]}...")
        try:
            st.json(json.loads(block.data))
        except:
            st.write(block.data)
        st.markdown("---")
