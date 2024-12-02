import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import streamlit as st
from streamlit_chat import message
import base64
import re

class ChatHistory:

    def __init__(self):
        """
        Initialize chat history from session state.
        """
        self.history = st.session_state.get("history", [])
        st.session_state["history"] = self.history

        # 상품명 버튼을 위한 index
        self.b_idx = 0

    def default_greeting(self):
        """
        Default greeting message for the user.
        """
        return "안녕! Save Mate! 👋"

    def image_to_base64(self, image_path):
        """
        Convert an image file to a base64 string for display in HTML.
        """
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_string

    def default_prompt(self):
        """
        Default prompt message for the assistant.
        """
        return """
        Save Mate에 오신 걸 환영합니다! 
        금융 목표, 기간, 키워드를 입력하시면 맞춤형 금융 상품을 추천해드릴게요.
        질문 예시:
        - "6개월 동안 여행을 위한 적금을 추천해줘"
        - "군인에게 적합한 상품이 뭐야?"
        """

    def initialize_user_history(self):
        """
        Initialize user message history.
        """
        st.session_state["user"] = [self.default_greeting()]

    def initialize_assistant_history(self):
        """
        Initialize assistant message history.
        """
        st.session_state["assistant"] = [self.default_prompt()]

    def initialize(self):
        """
        Initialize history if not already set in session state.
        """
        if "assistant" not in st.session_state:
            self.initialize_assistant_history()
        if "user" not in st.session_state:
            self.initialize_user_history()

    def reset(self):
        """
        Reset chat history.
        """
        st.session_state["history"] = []
        self.initialize_user_history()
        self.initialize_assistant_history()
        st.session_state["reset_chat"] = False

    def append(self, mode, message):
        """
        Append a message to user or assistant history.
        """
        st.session_state[mode].append(message)

    def generate_messages(self, container):
        """
        Display the chat history.
        """
        if st.session_state["assistant"]:
            with container:
                for i in range(len(st.session_state["assistant"])):
                    # Display user message
                    message(
                        st.session_state["user"][i],
                        is_user=True,
                        key=f"history_{i}_user",
                        avatar_style="big-smile",
                    )
                    # Display assistant message
                    message(
                        st.session_state["assistant"][i],
                        key=str(i),
                        avatar_style="identicon",
                    )
