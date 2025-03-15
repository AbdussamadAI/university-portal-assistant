import streamlit as st  # Used for UI components
import subprocess
import sys
import os

# Install required packages for Hugging Face Space
subprocess.check_call([sys.executable, "-m", "pip", "install", "agno", "openai", "python-dotenv"])

# Set environment variables for Hugging Face Space
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()
else:
    # For Hugging Face Spaces, set a placeholder API key
    # The actual key should be set in the Space's secrets
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "placeholder")

# Import the main app
from university_portal_app import main

# Run the app
if __name__ == "__main__":
    st.title("University Portal Assistant")
    main()
