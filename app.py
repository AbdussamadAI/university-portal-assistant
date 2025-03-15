import streamlit as st  # Used for UI components
import subprocess
import sys
import os

# Install required packages for Hugging Face Space
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "agno", "openai", "python-dotenv"])
    print("Successfully installed required packages")
except Exception as e:
    print(f"Error installing packages: {e}")
    # Continue anyway as packages might be pre-installed in the environment

# Set environment variables for Hugging Face Space
if os.path.exists(".env"):
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded environment variables from .env file")
    except Exception as e:
        print(f"Error loading .env file: {e}")
else:
    # For Hugging Face Spaces, get the API key from secrets
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY not found in environment variables. Please add it to your Hugging Face Space secrets.")
        st.stop()
    else:
        print("Using OPENAI_API_KEY from environment variables")

# Import the main app
try:
    from university_portal_app import main
    print("Successfully imported main function from university_portal_app")
except Exception as e:
    st.error(f"Error importing main function: {e}")
    st.stop()

# Run the app
if __name__ == "__main__":
    st.title("University Portal Assistant")
    try:
        main()
    except Exception as e:
        st.error(f"Error running the application: {e}")
        st.write("Please check the logs for more details.")
