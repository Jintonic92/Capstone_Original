import os
import streamlit as st
from modules.history import ChatHistory
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar

from langchain_core.messages import HumanMessage, AIMessage

# Reload modules for local updates
def reload_module(module_name):
    import importlib
    import sys
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    return sys.modules[module_name]

# Reload and import required modules
history_module = reload_module('modules.history')
layout_module = reload_module('modules.layout')
utils_module = reload_module('modules.utils')
sidebar_module = reload_module('modules.sidebar')

ChatHistory = history_module.ChatHistory
Layout = layout_module.Layout
Utilities = utils_module.Utilities
Sidebar = sidebar_module.Sidebar

# Set page configuration
st.set_page_config(layout="wide", page_icon="💬", page_title="금융상품 추천 | Save Mate")

# Initialize layout, sidebar, and utilities
layout = Layout()
sidebar = Sidebar()
utils = Utilities()

# Display the header
layout.show_header("금융상품을")

# Sidebar reset chat button
sidebar.show_options()

# Load the API key
user_api_key = utils.load_api_key()

if not user_api_key:
    layout.show_api_key_missing()
else:
    os.environ["UPSTAGE_API_KEY"] = user_api_key

    # Initialize chatbot if not already set
    if "chatbot" not in st.session_state:
        chatbot = utils.setup_chatbot()
    else:
        chatbot = st.session_state["chatbot"]

    # Initialize chat history
    history = ChatHistory()
    history.initialize()

    # Create containers for responses and input forms
    response_container, prompt_container = st.container(), st.container()

    with prompt_container:
        # Display the prompt form and collect user inputs
        submit_button, target_period, installation_amount, keywords, user_input = layout.prompt_form()

        # Reset chat if requested
        if st.session_state["reset_chat"]:
            history.reset()

        # Handle user query submission
        if submit_button and user_input:
            # Append user query to history
            history.append("user", user_input)

            # Prepare query and retrieve context
            query = f"{user_input.lower()}"
            context = chatbot.retrieve_documents(query, target_period, keywords)

            # Generate chatbot response
            chat_history = st.session_state.get("history", [])
            output = chatbot.generate_responses(user_input, context, chat_history, target_period, keywords)

            # Update history with the response
            st.session_state["history"] += [HumanMessage(query), AIMessage(output)]
            history.append("assistant", output)

    # Display chat history
    history.generate_messages(response_container)
