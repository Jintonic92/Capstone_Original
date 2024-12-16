import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import streamlit as st
from streamlit_chat import message
import base64
import re

class ChatHistory:
    def __init__(self):
        self.history = st.session_state["history"]  # 세션 상태의 history를 참조
        self.b_idx = 0  # 상품명 버튼 인덱스

    def default_greeting(self):
        return "안녕! Save Mate! 👋"

    def image_to_base64(self, image_path): 
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_string

    def default_prompt(self, topic):
        image_path = "./src/modules/img_folder/free-icon-golden-retriever-5374233.png"
        encoded_image = self.image_to_base64(image_path)

        prompt_text = f"""사이드바에서 유저아이디/금융상품종류를 입력해주세요. 입력하지 않으면 게스트모드/일반채팅모드로 실행이 됩니다.
        정확한 정보를 안내해 드리기 위해 열심히 학습하고 있지만, 가끔은 실수를 할 수도 있습니다.
        <br><br>
        <img src="data:image/png;base64,{encoded_image}" alt="Financial Image" style="width:150px;"><br>
        """
        return prompt_text
    
    def extract_product_names(self, response):
        product_pattern = re.compile(r"(은행명\s*:\s*(.*?)\n)?상품명\s*:\s*(.*?)\n")
        matches = product_pattern.findall(response)
        product_names = [match[2] if not match[1] else f"{match[1]} {match[2]}" for match in matches]
        return product_names

    def process_assistant_response(self, response_text):
        product_names = self.extract_product_names(response_text)
        st.markdown(f"""
        <div style="background-color: #001F3F; padding: 10px; border-radius: 10px; color: white;">
            {response_text}
        </div>
        """, unsafe_allow_html=True)

        user_message = None
        if product_names:
            st.write("상품 정보를 클릭해 추가 정보를 확인하세요.")
            for idx, product in enumerate(product_names):
                if st.button(product, key=f"product_button_{idx + self.b_idx}"):
                    user_message = f"{product} 상품을 확인하고 싶어"
            self.b_idx += 10
        return user_message

    def initialize_user_history(self):
        if not st.session_state["user"]:
            st.session_state["user"] = [self.default_greeting()]

    def initialize_assistant_history(self, topic):
        if not st.session_state["assistant"]:
            st.session_state["assistant"] = [self.default_prompt(topic)]

    def initialize(self, topic):
        self.initialize_user_history()
        self.initialize_assistant_history(topic)

    def reset(self):
        st.session_state["history"] = []
        self.initialize_user_history()
        self.initialize_assistant_history("topic")
        st.session_state["reset_chat"] = False

    def append(self, mode, message):
        st.session_state[mode].append(message)

    def generate_messages(self, container):
        if st.session_state["assistant"]:
            with container:
                for i in range(len(st.session_state["assistant"])):
                    message(
                        st.session_state["user"][i],
                        is_user=True,
                        key=f"history_{i}_user",
                        avatar_style="big-smile",
                    )
                    message(
                        st.session_state["assistant"][i],
                        key=str(i),
                        avatar_style="identicon",
                    )
