import streamlit as st
import os
import sys

# App version
APP_VERSION = "1.0.1"

# Set page config
st.set_page_config(
    page_title="University Portal Assistant",
    page_icon="🎓",
    layout="wide"
)

# Display a message while loading
st.markdown(f"## 🎓 University Portal Assistant v{APP_VERSION}")
st.markdown("Loading application... Please wait.")

# Check for OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ OPENAI_API_KEY not found in environment variables.")
    st.info("Please add your OpenAI API key to the Hugging Face Space secrets.")
    st.stop()

# Install required packages
with st.spinner("Installing required packages..."):
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", 
                              "agno", "openai", "python-dotenv", "pandas"])
        st.success("✅ Successfully installed required packages")
    except Exception as e:
        st.warning(f"⚠️ Note: {e}")
        st.info("Continuing anyway as packages might be pre-installed")

# Import the main app
try:
    from university_portal_app import main
    
    # Run the main application
    main()
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.info("Please check the application logs for more details.")
    
    # Display detailed error information
    import traceback
    st.code(traceback.format_exc(), language="python")
