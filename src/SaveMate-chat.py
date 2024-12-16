import os
import streamlit as st
from modules.history import ChatHistory
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar
from langchain_core.messages import HumanMessage, AIMessage

# Streamlit 페이지 설정
st.set_page_config(layout="wide", page_icon="💬", page_title="금융상품 추천해주는 | Save Mate")

# 컴포넌트 초기화
layout = Layout()
layout.show_header("금융상품을")
utils = Utilities()
sidebar_module = Sidebar()

# 세션 상태 초기화 함수
def initialize_session_state():
    default_keys = {
        "history": [],
        "ready": False,
        "product_type": None,
        "chatbot": None,
        "user": [],
        "user_id": None,
        "user_message": None,
        "assistant": [],
        "reset_chat": False,
        "api_key": None,
    }
    for key, default_value in default_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# 세션 상태 초기화
initialize_session_state()

# API 키 로드
user_api_key, langsmith_api_key = utils.load_api_key()

if not user_api_key:
    layout.show_api_key_missing()
else:
    os.environ["UPSTAGE_API_KEY"] = user_api_key

    # 챗봇 초기화
    if st.session_state["chatbot"] is None:
        st.session_state["chatbot"] = utils.setup_chatbot()
    # Sidebar에서 User ID를 가져옴
    Sidebar.get_user_id()

    # User ID 없을 경우 경고 출력
    if not st.session_state["user_id"]:
        st.warning("User ID가 필요합니다. 사이드바에서 User ID를 입력해주세요.")

    # Step 1: 금융상품 종류 선택
    if st.session_state["product_type"] is None:
        st.subheader("먼저 금융상품 종류를 선택해주세요.")
        product_type = st.radio(
            "추천받을 금융 상품 종류를 선택하세요:",
            ("추천 외 질문", "예금", "적금", "예금 & 적금"),
            index=0,
            key="product_type_selection",
        )

        if st.button("확인"):
            st.session_state["product_type"] = product_type
            st.session_state["ready"] = True
            st.experimental_rerun()  # 선택 후 페이지 새로고침

    # Step 2: 채팅 창 표시
    elif st.session_state["ready"]:
        st.write(f"선택된 금융상품 종류: {st.session_state['product_type']}")
        response_container, prompt_container = st.container(), st.container()

        history = ChatHistory()

        if st.session_state["reset_chat"]:
            history.reset()
            st.session_state["reset_chat"] = False

        with prompt_container:
            is_ready, user_input = layout.prompt_form()

            if is_ready:
                user_id = st.session_state.get("user_id", None)
                if not user_id:
                    st.warning("No User ID provided. Continuing in Guest Mode.")
                
                history.append("user", user_input)

                question = user_input
                query = f"{question.lower()}"
                product_type = st.session_state.get("product_type", "적용안함")  # 선택된 상품 유형 가져오기
                context = st.session_state["chatbot"].retrieve_documents(query, product_type=product_type)  # product_type 전달
                #context = st.session_state["chatbot"].retrieve_documents(query, product_type)
                chat_history = st.session_state.get("history", [])

                output = st.session_state["chatbot"].generate_responses(
                    question, context, chat_history, user_id=user_id, product_type=st.session_state["product_type"]
                )

                st.session_state["history"] += [HumanMessage(query), AIMessage(output)]
                history.append("assistant", output)
                history.generate_messages(response_container)
