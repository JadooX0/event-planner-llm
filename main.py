import streamlit as st
import os
import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


load_dotenv()


SELECTED_MODEL = "qwen/qwen2.5-vl-72b-instruct" 

llm = ChatOpenAI(
    model=SELECTED_MODEL, 
    api_key=st.secrets["OPENROUTER_API_KEY"],
    openai_api_base="https://openrouter.ai/api/v1",
    max_tokens=500, 
    default_headers={
        "HTTP-Referer": "http://localhost:8501", 
        "X-Title": "Event Planner Assistant"
    }
)

def encode_image(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode('utf-8')

st.title("MACS Event Planner")
st.subheader(f"Powered by {SELECTED_MODEL.split('/')[-1]}")

uploaded_file = st.file_uploader("Upload Event Poster", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Poster", width=300)
    
    if st.button("Analyze Poster"):
        base64_image = encode_image(uploaded_file)
        
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Extract: Event Name, Date, Time, Venue, and Ticket Price from this poster. Format as a clean list."},
                {
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        )
        
        with st.spinner(f"{SELECTED_MODEL.split('/')[-1]} is reading the poster..."):
            try:
                response = llm.invoke([message])
                st.success("Analysis Complete!")
                st.markdown(response.content)
            except Exception as e:
                st.error(f"Error: {e}")

