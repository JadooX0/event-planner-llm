import streamlit as st
import os
import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

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


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "poster_base64" not in st.session_state:
    st.session_state.poster_base64 = None
if "analysis_successful" not in st.session_state:
    st.session_state.analysis_successful = False

uploaded_file = st.file_uploader("Upload Event Poster", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Poster", width=300)
    st.session_state.poster_base64 = encode_image(uploaded_file)
    
    if st.button("Analyze Poster"):
        base64_image = st.session_state.poster_base64
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Extract: Event Name, Date, Time, Venue, and Ticket Price from this poster. Format as a clean list."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        )
        
        with st.spinner("Reading poster details..."):
            try:
                response = llm.invoke([message])
                analysis_text = response.content
                
                
                
                if analysis_text.count("Not provided") >= 3 or "no text" in analysis_text.lower():
                    st.session_state.analysis_successful = False
                    st.error("This image does not appear to be an event poster. Chatbot disabled.")
                else:
                    st.session_state.analysis_successful = True
                    st.success("Event detected! Chatbot enabled.")
                
                st.markdown(analysis_text)
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.subheader("Chat with the Assistant")


for msg in st.session_state.chat_history:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)


if user_query := st.chat_input("Ask a question about the poster..."):
    if st.session_state.poster_base64 is None:
        st.warning("Please upload a poster first!")
    else:
        
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        with st.chat_message("user"):
            st.markdown(user_query)

        
        with st.chat_message("assistant"):
            if not st.session_state.analysis_successful:
                block_msg = "I cannot answer questions about this image because it was not identified as a valid event poster."
                st.error(block_msg)
                
                st.session_state.chat_history.append(AIMessage(content=block_msg))
            else:
                
                with st.spinner("Thinking..."):
                    try:
                        current_payload = [
                            {"type": "text", "text": user_query},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.poster_base64}"}}
                        ]
                        
                        memory_context = st.session_state.chat_history[-5:]
                        response = llm.invoke(memory_context + [HumanMessage(content=current_payload)])
                        
                        st.markdown(response.content)
                        st.session_state.chat_history.append(AIMessage(content=response.content))
                    except Exception as e:
                        st.error(f"Chat Error: {e}")
