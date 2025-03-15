import streamlit as st
import os
import csv
import pandas as pd
import re
import io
import sys
from datetime import datetime
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="University Portal Assistant",
    page_icon="🎓",
    layout="wide"
)

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# File paths
UNANSWERED_QUESTIONS_FILE = "unanswered_questions.csv"
FAQ_FILE = "university_portal_faqs.csv"

# Ensure the CSV file exists with headers
if not os.path.exists(UNANSWERED_QUESTIONS_FILE):
    with open(UNANSWERED_QUESTIONS_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Question', 'Status'])

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to save unanswered questions
def save_unanswered_question(question):
    with open(UNANSWERED_QUESTIONS_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), question, "Pending"])
    return "Your question has been forwarded to a human representative. Someone will contact you soon."

# Initialize the agent
@st.cache_resource
def get_agent():
    return Agent(
        model=OpenAIChat(id="gpt-4o"),
        description="You are a University Portal Guide assistant!",
        instructions=[
            "You are a specialized chatbot for the University Student/Staff Portal.",
            "Your purpose is to answer frequently asked questions about the portal, registration, and related issues.",
            "Only answer questions that are within your knowledge base about the university portal and registration process.",
            "If a question is about the portal but you don't have the information, inform the user that the question will be forwarded to a human representative.",
            "If a question is not related to the university portal or registration, politely inform the user that you can only assist with portal-related queries.",
            "Be concise, helpful, and professional in your responses.",
            "Do not make up information that is not in your knowledge base.",
            "When answering questions, maintain a professional, friendly tone appropriate for a university setting."
        ],
        show_tool_calls=False,
        markdown=True
    )

# Get the agent instance
agent = get_agent()

# Load FAQ data
def load_faqs():
    faqs = {}
    if os.path.exists(FAQ_FILE):
        with open(FAQ_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                faqs[row['question'].lower()] = row['answer']
    
    # If no FAQs were loaded, provide some default ones
    if not faqs:
        st.warning("Warning: No FAQs loaded from file. Using default FAQs.")
        faqs = {
            "how to reset password?": "Try the default password (umstad@2025).",
            "how to change my name?": "Submit your details at MIS.",
            "how to change my level?": "Your level will change when your results are uploaded and approved.",
            "how to reset payment (50% or 100%)?": "Send your signed admission letter and your JAMB no (new student) or ID number (returning student).",
            "how to upload photo?": "Check my catalog in my profile.",
            "how to pay school fees?": "Check my catalog in my profile.",
            "why are my results not showing on the portal?": "Go to results/status and select the session.",
            "i paid but couldn't print permit": "Submit your Remita receipt at student affairs.",
            "my payment is showing pending": "Click on verify invoice and insert your RRR No (e.g. 1234556778)."
        }
    
    return faqs

# Function to find the best matching FAQ
def find_best_matching_faq(query, faqs):
    query = query.lower().strip()
    
    # First, try exact keyword matching
    keywords = {
        "password reset": "how to reset password?",
        "reset password": "how to reset password?",
        "change name": "how to change my name?",
        "name change": "how to change my name?",
        "change level": "how to change my level?",
        "level change": "how to change my level?",
        "payment reset": "how to reset payment (50% or 100%)?",
        "reset payment": "how to reset payment (50% or 100%)?",
        "upload photo": "how to upload photo?",
        "photo upload": "how to upload photo?",
        "pay fees": "how to pay school fees?",
        "school fees": "how to pay school fees?",
        "make payment": "how to pay school fees?",
        "payment": "how to pay school fees?",
        "how to pay": "how to pay school fees?",
        "results not showing": "why are my results not showing on the portal?",
        "can't see results": "why are my results not showing on the portal?",
        "paid but no permit": "i paid but couldn't print permit",
        "can't print permit": "i paid but couldn't print permit",
        "payment pending": "my payment is showing pending",
        "pending payment": "my payment is showing pending",
    }
    
    # Check for keyword matches
    for key, faq_question in keywords.items():
        if key in query:
            return faqs.get(faq_question)
    
    # If no keyword match, try more flexible matching with additional payment handling
    for question, answer in faqs.items():
        question_lower = question.lower()
        
        # More flexible matching
        if (query in question_lower or 
            question_lower in query or 
            any(word in query.split() for word in question_lower.split() if len(word) > 3)):
            return answer
    
    # Special case for payment-related queries that might not match exactly
    if any(payment_term in query for payment_term in ["pay", "payment", "fee", "fees", "money", "tuition"]):
        return faqs.get("how to pay school fees?")
    
    # If no match found in FAQs, check if it's portal-related
    portal_keywords = [
        "password", "reset", "name", "level", "payment", "photo", "fees", 
        "results", "permit", "invoice", "rrr", "portal", "registration", 
        "student", "staff", "login", "account", "pay", "tuition", "money"
    ]
    
    # Check if query contains any portal-related keywords
    is_portal_related = any(keyword in query for keyword in portal_keywords)
    
    if is_portal_related:
        # It's a portal question but not in FAQs, forward to human
        return None  # Will be forwarded to human rep
    else:
        # Not a portal-related question
        return "I'm sorry, I can only answer questions related to the university portal, registration, and student/staff services. If you have questions about these topics, please feel free to ask."

# Function to enhance response using OpenAI
def enhance_response(query, base_answer):
    if base_answer is None:
        return save_unanswered_question(query)
    
    # Use the global agent instance
    # No need to call get_agent() again since we already have the agent instance
    
    # Use the agent to enhance the response
    prompt = f"""
    Question: {query}
    
    Basic Answer: {base_answer}
    
    Please provide a more professional, helpful response to the question while maintaining the same factual information. 
    Be concise but friendly, and format your response appropriately for a university setting.
    """
    
    try:
        # Capture the printed response by redirecting stdout
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        
        # Call print_response with stream=False to get the entire response at once
        agent.print_response(prompt, stream=False)
        
        # Get the captured output and restore stdout
        sys.stdout = old_stdout
        enhanced_response = new_stdout.getvalue()
        
        # Extract just the response part (after the prompt)
        if "Response" in enhanced_response:
            # Find the response section
            response_parts = enhanced_response.split("Response")
            if len(response_parts) > 1:
                # Get everything after "Response"
                response_text = "Response" + response_parts[1]
                # Clean up the formatting
                # Remove ANSI color codes and box characters
                clean_response = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', response_text)
                clean_response = re.sub(r'[┃┏┓┗┛━]', '', clean_response)
                # Remove any remaining whitespace and newlines
                clean_response = clean_response.strip()
                # Remove the "Response (x.xs)" part
                clean_response = re.sub(r'Response \([0-9.]+s\)', '', clean_response)
                enhanced_response = clean_response.strip()
        
        # Log the responses for debugging
        st.session_state.debug_info = {
            "original_query": query,
            "base_answer": base_answer,
            "enhanced_answer": enhanced_response
        }
        
        # If we couldn't extract a clean response, or if it's too short, return the original
        if not enhanced_response or len(enhanced_response) < len(base_answer):
            return base_answer
        
        return enhanced_response
    except Exception as e:
        st.error(f"Error enhancing response: {e}")
        return base_answer

# Function to process user input
def process_query(query, faqs):
    try:
        # Try to find a matching FAQ
        base_response = find_best_matching_faq(query, faqs)
        
        # Show a spinner while enhancing the response
        with st.spinner("Enhancing response with AI..."):
            # Enhance the response using OpenAI
            return enhance_response(query, base_response)
    except Exception as e:
        st.error(f"Error processing query: {e}")
        return save_unanswered_question(query)

# Main UI layout
def main():
    # Custom CSS
    st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .chat-message {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
    }
    .user {
        background-color: #e6f7ff;
        border-left: 5px solid #1890ff;
    }
    .bot {
        background-color: #f6ffed;
        border-left: 5px solid #52c41a;
    }
    .stButton button {
        width: 100%;
        border-radius: 20px;
    }
    .app-header {
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Load FAQs
    faqs = load_faqs()
    
    # Initialize session state for messages if not already done
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Header
    st.markdown('<div class="app-header"><h1>🎓 University Portal Assistant</h1></div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=150)
        st.title("University Portal Assistant")
        st.markdown("---")
        
        st.subheader("About")
        st.markdown("""
        This assistant helps you navigate the University Portal and answers frequently asked questions about registration, payments, and other portal-related issues.
        
        **Powered by OpenAI's GPT-4o model** to provide detailed, helpful responses.
        """)
        
        st.markdown("---")
        
        # Show FAQ section in sidebar
        st.subheader("Common FAQs")
        
        # Display a few common FAQs
        common_faqs = [
            ("How to reset password?", "Try the default password (umstad@2025)."),
            ("How to change my name?", "Submit your details at MIS."),
            ("How to pay school fees?", "Check my catalog in my profile.")
        ]
        
        for question, answer in common_faqs:
            with st.expander(question):
                st.write(answer)
        
        st.markdown("---")
        
        # Admin section - View unanswered questions
        st.subheader("Admin Section")
        if st.button("View Unanswered Questions"):
            try:
                unanswered_df = pd.read_csv(UNANSWERED_QUESTIONS_FILE)
                st.dataframe(unanswered_df)
            except Exception as e:
                st.error(f"Error loading unanswered questions: {e}")
                
        # Add debug toggle
        st.markdown("---")
        st.subheader("Debug Options")
        if st.checkbox("Show Response Debug Info"):
            if "debug_info" in st.session_state:
                st.subheader("Original Query")
                st.write(st.session_state.debug_info["original_query"])
                st.subheader("Base Answer (from CSV)")
                st.write(st.session_state.debug_info["base_answer"])
                st.subheader("Enhanced Answer (from AI)")
                st.write(st.session_state.debug_info["enhanced_answer"])
    
    # Input field at the top
    st.subheader("Ask a question about the university portal:")
    
    # Use a form for Enter key handling
    with st.form(key="query_form", clear_on_submit=True):
        # Input and button in columns
        col1, col2 = st.columns([5, 1])
        
        with col1:
            query = st.text_input("Query", placeholder="Type your question here...", key="query_input", label_visibility="collapsed")
        
        with col2:
            send_button = st.form_submit_button("Send")
    
    # Add a divider between input and chat
    st.markdown("---")
    
    # Process the query when the form is submitted
    if send_button and query:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Show spinner while processing
        with st.spinner("Processing your question..."):
            # Process the query
            response = process_query(query, faqs)
        
        # Add bot response to chat history
        st.session_state.messages.append({"role": "bot", "content": response})
        
        # Use st.rerun() instead of the deprecated st.experimental_rerun()
        st.rerun()
    
    # Display chat messages from history
    st.subheader("Conversation:")
    
    # If no messages yet, show a placeholder
    if not st.session_state.messages:
        st.info("Your conversation will appear here after you ask a question.")
    
    # Display the conversation
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot"><strong>Assistant:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.8rem;">
        2025 University Portal Assistant | Powered by Agno AI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
