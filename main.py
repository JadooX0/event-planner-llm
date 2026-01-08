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

def clear_chat_history():
    
    st.session_state.chat_history = []
    st.session_state.analyzer_result = ""
    st.rerun()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "poster_base64" not in st.session_state:
    st.session_state.poster_base64 = None
if "analyzer_result" not in st.session_state:
    st.session_state.analyzer_result = ""

uploaded_file = st.file_uploader("Upload Event Poster", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Poster", width=300)
    st.session_state.poster_base64 = encode_image(uploaded_file)
    
    
    if st.button("Start Analysis"):
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Extract: Event Name, Date, Time, Venue, and Ticket Price from this poster. Format as a clean list."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.poster_base64}"}}
            ]
        )
        
        with st.spinner("Analyzing poster..."):
            try:
                response = llm.invoke([message])
                st.session_state.analyzer_result = response.content
                st.session_state.chat_history.append(AIMessage(content=response.content))
                st.success("Initial Analysis Complete!")
            except Exception as e:
                st.error(f"Analysis Error: {e}")

st.divider()


for msg in st.session_state.chat_history:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)


def analysis_is_failed():
    
    failure_keywords = ["could not find", "no details detected", "blurry", "unable to read", "cannot see"," Not provided in the image."]
    
    
    if not st.session_state.analyzer_result:
        return True
    return any(word in st.session_state.analyzer_result.lower() for word in failure_keywords)


if user_query := st.chat_input("Ask a follow-up question..."):
    if st.session_state.poster_base64 is None:
        st.warning("Please upload a poster first!")
    else:
        
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))

        with st.chat_message("assistant"):
            
            if analysis_is_failed():
                error_feedback = "**Access Denied:** I cannot answer questions because the initial poster analysis failed to extract required details. Please upload a clearer image."
                st.error(error_feedback)
                st.session_state.chat_history.append(AIMessage(content=error_feedback))
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
