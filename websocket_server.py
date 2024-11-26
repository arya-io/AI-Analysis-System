import asyncio
import websockets
from difflib import SequenceMatcher
from langchain_groq import ChatGroq  # Import the ChatGroq class

# Cache for storing processed responses
cache = {}

# Initialize the LLM (replace with your actual Groq API key and model name)
llm = ChatGroq(temperature=0.7, groq_api_key=["groq_api_key"], model_name="llama3-70b-8192")

# Function to compare similarity between two strings (for fallback if needed)
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Feedback generation using LLM
async def generate_feedback_with_llm(question, user_answer):
    # Create the messages to pass to the LLM
    messages = [
        (
            "system",
            "You are an AI tutor providing detailed feedback on student answers to AI-related questions.",
        ),
        ("human", f"Question: {question}\nStudent's Answer: {user_answer}"),
    ]
    
    # Invoke the LLM to get feedback
    ai_msg = llm.invoke(messages)
    
    feedback = ai_msg.content
    return feedback

# Fallback feedback generation using similarity
def generate_feedback(question, user_answer):
    # Define correct answers for simplicity
    correct_answers = {
        "What is a neural network?": "A neural network is a model inspired by biological networks.",
        "What is supervised learning?": "Supervised learning uses labeled data for training."
    }
    
    # Handle invalid or unrecognized questions
    if question not in correct_answers:
        return "Score: 0/10\nFeedback: This question is not recognized. Please try a different question."
    
    # Handle empty or nonsensical answers
    if not user_answer or len(user_answer.strip()) == 0:
        return "Score: 0/10\nFeedback: The answer provided is empty. Please provide a valid response."
    
    # Get the correct answer
    correct_answer = correct_answers[question]
    
    # Compute the similarity between the user's answer and the correct answer
    score = similarity(correct_answer, user_answer)
    
    # Generate feedback based on the similarity score
    if score > 0.8:
        return "Score: 10/10\nFeedback: Your answer is correct and thorough."
    elif score > 0.5:
        return "Score: 7/10\nFeedback: Good attempt, but your answer is slightly incomplete or inaccurate. Review the concept."
    else:
        return "Score: 5/10\nFeedback: Good attempt, but your answer is incomplete or inaccurate. Review the concept."

# WebSocket handler for processing student responses
async def handle_student_response(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")
        
        try:
            # Split message into question and response
            question, answer = message.split("|")
        except ValueError:
            await websocket.send("Error: Invalid message format. Please provide both a question and a response.")
            continue

        # Cache lookup
        cache_key = (question, answer)
        if cache_key in cache:
            print(f"Cache hit for {cache_key}")
            feedback = cache[cache_key]
        else:
            print(f"Cache miss for {cache_key}")
            # Use the LLM to generate feedback
            feedback = await generate_feedback_with_llm(question, answer)
            cache[cache_key] = feedback  # Cache the result

        # Send feedback back to client
        await websocket.send(f"Processed response for question: '{question}'\n{feedback}")

# WebSocket server setup to handle concurrent connections
async def start_server():
    async with websockets.serve(handle_student_response, "localhost", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.Future()  # Keep server running forever

# Handle WebSocket timeouts gracefully
async def handle_websocket_timeout(websocket, timeout=5):
    try:
        # Wait for the WebSocket message with a timeout
        message = await asyncio.wait_for(websocket.recv(), timeout=timeout)
        return message
    except asyncio.TimeoutError:
        return "Timeout: The server took too long to respond."

# Run the server
if __name__ == "__main__":
    asyncio.run(start_server())
