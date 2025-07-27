import streamlit as st
from openai import OpenAI, RateLimitError
import base64
from PIL import Image
import io
import time

st.set_page_config(page_title="We help you with math")
st.title("🧮 We help you with math (MOE Syllabus)")

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Upload image
uploaded_file = st.file_uploader("Upload a photo of your math question", type=["jpg", "jpeg", "png"])
image_base64 = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded image", use_column_width=True)
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

# Chat input
if prompt := st.chat_input("Ask a math question..."):
    if image_base64:
        st.session_state.messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]
        })
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})

    # Retry logic
    response = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a math tutor who explains step-by-step using the Singapore MOE syllabus. "
                            "Use clean markdown with LaTeX formatting for math expressions. Use headers and bullet points if needed."
                        )
                    }
                ] + st.session_state.messages
            )
            break
        except RateLimitError:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                st.error("Rate limit exceeded. Please try again later.")
                st.stop()

    if response:
        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})

# Render messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        content = msg["content"]

        if isinstance(content, list):  # image + text
            for part in content:
                if part.get("type") == "text":
                    blocks = part["text"].split("\n\n")
                    for block in blocks:
                        block = block.strip()
                        if block.startswith("$$") and block.endswith("$$"):
                            st.latex(block[2:-2])
                        elif block.startswith(r"\[") and block.endswith(r"\]"):
                            st.latex(block[2:-2])
                        elif block.startswith("$") and block.endswith("$"):
                            st.latex(block[1:-1])
                        elif "\\begin" in block:
                            st.latex(block)
                        elif block.strip().startswith("```") and block.strip().endswith("```"):
                            st.code(block.strip("`"), language="python")
                        else:
                            st.markdown(block)
                elif part.get("type") == "image_url":
                    st.image(part["image_url"]["url"])
        elif isinstance(content, str):  # plain text or LaTeX
            blocks = content.split("\n\n")
            for block in blocks:
                block = block.strip()
                if block.startswith("$$") and block.endswith("$$"):
                    st.latex(block[2:-2])
                elif block.startswith(r"\[") and block.endswith(r"\]"):
                    st.latex(block[2:-2])
                elif block.startswith("$") and block.endswith("$"):
                    st.latex(block[1:-1])
                elif "\\begin" in block:
                    st.latex(block)
                elif block.strip().startswith("```") and block.strip().endswith("```"):
                    st.code(block.strip("`"), language="python")
                else:
                    st.markdown(block)
