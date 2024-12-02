import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import streamlit as st
from modules.chatbot import Chatbot
from modules.embedder import Embedder
from dotenv import load_dotenv

class Utilities:
    @staticmethod
    def load_api_key():
        """
        Load the API key from the .env file.
        """
        if not hasattr(st.session_state, "api_key"):
            st.session_state.api_key = None

        load_dotenv()
        user_api_key = os.getenv("UPSTAGE_API_KEY")

        if not user_api_key:
            st.error("API key not found! Please set it in the .env file.")
        return user_api_key

    @staticmethod
    def setup_chatbot():
        """
        Set up the chatbot with retrievers for different product types.
        """
        embeds = Embedder()

        # Create retrievers for different product types
        retriever_예금 = embeds.get_retriever('예금')
        retriever_적금 = embeds.get_retriever('적금')
        retriever_예금_적금 = embeds.get_retriever('예금 & 적금')

        # Initialize the chatbot
        chatbot = Chatbot(retriever_예금, retriever_적금, retriever_예금_적금)

        # Save chatbot in session state
        st.session_state["chatbot"] = chatbot
        st.session_state["ready"] = True

        print("Chatbot setup complete.")
        return chatbot

    @staticmethod
    def validate_user_inputs():
        """
        Validate user inputs for target period, installation amount, and keywords.
        """
        target_period = st.session_state.get("target_period")
        installation_amount = st.session_state.get("installation_amount")
        keywords = st.session_state.get("keywords")

        if not target_period or not installation_amount or not keywords:
            st.warning("Please provide all required inputs: target period, amount, and keywords.")
            return False

        print(f"Inputs validated: Target Period: {target_period}, Installation Amount: {installation_amount}, Keywords: {keywords}")
        return True
