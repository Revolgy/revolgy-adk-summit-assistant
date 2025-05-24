import streamlit as st
import requests
import os
import uuid

API_URL = os.getenv("API_URL", "http://0.0.0.0:8000")

st.set_page_config(page_title="Revolgy Google Cloud Summit Assistant", layout="centered", initial_sidebar_state="collapsed")

add_navbar = f"""
<nav class="navbar sticky-header">
    <div class="navbar-container">
        <a href="https://revolgy.com" target="_blank" class="navbar-logo">
            <img src="https://www.revolgy.com/hs-fs/hubfs/revolgy%20logo%20-%20white%20190.png" alt="Revolgy Logo">        
        </a>
</nav>
"""

st.markdown(add_navbar, unsafe_allow_html=True)

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stAppDeployButton {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# Load external CSS
def load_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Call the function to load the CSS
load_css("style.css")

#st.image("assets/revolgy_logo.png", width=100, use_container_width=True)

st.markdown(
    """
    <div style="display: flex; gap: 1.5rem; justify-content: center; align-items: center; padding: 1rem 0;">
        <a href="https://revolgy.com" target="_blank" style="color: #FFD700; text-decoration: none; font-weight: bold;">🔗 revolgy.com</a>
        <a href="https://github.com/non-existent-repo" target="_blank" style="color: white; text-decoration: none; font-weight: bold; display: flex; align-items: center;">
            <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/github.svg" width="18" height="18" alt="GitHub" style="filter: invert(48%) sepia(100%) saturate(700%) hue-rotate(230deg) brightness(105%) contrast(95%); margin-right: 0.1rem;">
            Get the code for this app!
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="text-align: center; font-size: 1.2rem; margin-bottom: 1.5rem;">
        <h3>Google Cloud Summit Prague 2025 Assistant</h3>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="button-row">
      <button class="how-it-works-btn">
        How does it work?
        <span class="how-it-works-tooltip">
            I am a multi-agent tool built with Google Agent Development Kit (ADK). 
            One agent reads the Cloud Summit agenda from a JSON file, another uses Vertex AI Search on Google Cloud documentation, 
            and a third performs general Google Searches.
        </span>
      </button>
      <button class="example-prompts-btn">
        Example prompts
        <span class="example-prompts-tooltip">
            • What time does the keynote start?<br>
            • Show me all the sessions about AI at the summit.<br>
            • Who are the speakers for session X?
        </span>
      </button>
      <button class="example-prompts-btn">
        Disclaimer
        <span class="example-prompts-tooltip disclaimer-tooltip">
            The assistant is for demo purposes and can make mistakes. 
            Its main purpose is to help with Google Cloud Summit Prague 2025 agenda and find information on Google Cloud services.
            It is not to be treated as a general purpose chatbot e.g. Gemini or ChatGPT. 
            Please verify the information.
        </span>
      </button>
    </div>
    """,
    unsafe_allow_html=True
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# React to user input
if user_input := st.chat_input("Hi attendees! How can I assist you today?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(user_input)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    session_id = st.session_state.session_id

    first_payload = {
        "name": "test",
    }

    response = requests.post(
            f"{API_URL}/apps/summit_app/users/user_001/sessions/{session_id}",
            json=first_payload,
            headers={"Content-Type": "application/json"}
    )

    # Prepare API request payload
    payload = {
        "app_name": "summit_app",
        "user_id": "user_001",
        "session_id": session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": user_input}]
        }
    }

    # Send the request to the API
    try:
        response = requests.post(
            f"{API_URL}/run",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        print(data)

        # Extract the `actions > state_delta > summit` field
        for item in data:
            if "actions" in item and "state_delta" in item["actions"] and "summit" in item["actions"]["state_delta"]:
                # Extract the value of the `summit` field
                bot_response = item["actions"]["state_delta"]["summit"]
                break
            elif "actions" in item and "stateDelta" in item["actions"] and "summit" in item["actions"]["stateDelta"]:
                # Extract the value of the `summit` field
                bot_response = item["actions"]["stateDelta"]["summit"]
                break

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(bot_response.strip())
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": bot_response.strip()})

    except requests.exceptions.RequestException as e:
        error_message = f"An error occurred. Please try again later. Error: {str(e)}"
        with st.chat_message("assistant"):
            st.markdown("There was an error processing your request. Please try again later.")
        st.session_state.messages.append({"role": "assistant", "content": "There was an error processing your request. Please try again later."})

# Footer
st.markdown(
    """
    <div style="text-align: center; margin-top: 2rem; font-size: 1rem; color: #FFD700;">
        <a href="https://revolgy.com/blog" target="_blank" style="color: #FFD700; text-decoration: none; font-weight: bold;">How did we build this?</a>
        <span style="margin: 0 1rem;">•</span>
        <a href="https://revolgy.com/contact" target="_blank" style="color: #FFD700; text-decoration: none; font-weight: bold;">Ask for a 1:1 with our engineer!</a>
    </div>
    """,
    unsafe_allow_html=True
)
