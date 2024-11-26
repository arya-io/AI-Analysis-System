import streamlit as st
import asyncio
import websockets

async def send_message(question, response):
    
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        message = f"{question}|{response}"
        await websocket.send(message)
        
        feedback = await websocket.recv()
        return feedback

st.set_page_config(
    page_title = 'AI Analysis System',
)
st.title("AI Analysis System")
st.write("Ask an AI-related question and provide your answer below:")

question = st.text_input("Enter AI-related question:")
response = st.text_area("Enter your response:")

if st.button("Submit"):
    if question and response:
        feedback = asyncio.run(send_message(question, response))
        
        st.write("Feedback from the server:")
        st.success(feedback)
    else:
        st.warning("Please provide both a question and a response.")
