import streamlit as st

# Set page config
st.set_page_config(
    page_title="University Portal Assistant",
    page_icon="🎓",
    layout="wide"
)

# Display a simple message
st.title("🎓 University Portal Assistant")
st.write("This is a minimal version of the app to test deployment.")
st.write("If you can see this message, the deployment is working!")

# Add a button to test interactivity
if st.button("Click me!"):
    st.success("Button clicked successfully!")
