import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io

st.set_page_config(page_title="We help you with math")
st.title("🧮 We help you with math (MOE Syllabus)")

# Initialize OpenAI client with the new SDK
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize session messages
if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader("Upload a photo of your math question", type=["jpg", "jpeg", "png"])
image_base64 = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded image", use_column_width=True)
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

if prompt := st.chat_input("Ask a math question..."):
    user_msg = prompt + ("\n(Attached image included)" if image_base64 else "")
    st.session_state.messages.append({"role": "user", "content": user_msg})

    # Request with new client syntax
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a math tutor who teaches step-by-step using the Singapore MOE syllabus from Primary to JC2. Be friendly and concise."},
        ] + st.session_state.messages
    )

    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
