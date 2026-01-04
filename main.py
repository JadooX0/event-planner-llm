import streamlit as st
import os
import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


load_dotenv()


import streamlit as st
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(
    model="google/gemini-3-flash-preview", 
    api_key=st.secrets["OPENROUTER_API_KEY"], 
    openai_api_base="https://openrouter.ai/api/v1"
)




def encode_image(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode('utf-8')

st.title("Gemini Event Planner")

uploaded_file = st.file_uploader("Upload Event Poster", type=["jpg", "png", "jpeg"])

if uploaded_file:
    
    st.image(uploaded_file, caption="Uploaded Poster", width=300)
    
    if st.button("Analyze Poster"):
        base64_image = encode_image(uploaded_file)
        
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Extract: Event Name, Date, Time, Venue, and Ticket Price from this poster. Format as a clean list."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        )
        
        with st.spinner("Gemini is reading the poster..."):
            try:
                response = llm.invoke([message])
                st.success("Analysis Complete!")
                st.markdown(response.content)
            except Exception as e:
                st.error(f"Error: {e}")