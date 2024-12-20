import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import streamlit as st

class Sidebar:

    @staticmethod
    def reset_chat_button():
        # "Reset chat" 버튼을 표시하고, 클릭되면 세션 상태의 "reset_chat"을 True로 설정
        if st.button("Reset chat"):
            st.session_state["reset_chat"] = True
        # 세션 상태에 "reset_chat"이 없을 경우 기본값 False로 설정
        st.session_state.setdefault("reset_chat", False)

    @staticmethod
    def get_user_id():
        # 사이드바에서 유저 ID를 입력 받는 부분
        with st.sidebar:
            st.header("User Information")
            st.subheader("Enter your User ID (required for personalized recommendations)")
            st.write("예시: user_0, user_1, user_2")

            # 세션 상태에 "user_id"가 없으면 입력란 표시
            if not st.session_state["user_id"]:
                user_id = st.text_input("User ID:", placeholder="Enter your User ID", key="user_id_input")
                if user_id:
                    st.session_state["user_id"] = user_id
                    st.success(f"User ID {user_id} has been set!")
                    print(f"User ID set: {user_id}")
                else:
                    st.warning("No User ID provided. General mode will be used.")
            else:
                # 유저 ID가 이미 있는 경우 표시
                st.sidebar.write(f"User ID: {st.session_state['user_id']}")
                st.sidebar.write("User ID를 다시 입력하려면 페이지를 새로고침 해주세요.")


    def show_options(self):
        # 사이드바에 대화 리셋 옵션을 표시
        with st.sidebar.expander("🛠️ 대화 리셋", expanded=False):
            self.reset_chat_button() # 리셋 버튼 표시


    @staticmethod
    def get_product_type():
        # 추천받을 금융 상품의 종류를 선택하는 부분
        with st.sidebar:
            st.subheader("어떤 금융상품을 추천받으시겠어요?")

            # radio 버튼의 레이블을 숨기기 위해 CSS 스타일을 적용
            st.markdown(
                """
                <style>
                .stRadio > label {
                    display: none;
                }
                .stRadio > div {
                    margin-top: -20px;
                }
                </style>
                """,
                unsafe_allow_html=True  # HTML 및 CSS를 사용 가능하도록 설정
            )
        
        # 세션에 product_type 값이 없다면 기본값 설정
            if 'product_type' not in st.session_state:
                st.session_state['product_type'] = '적용안함'  # 기본값 설정

            # 사용자가 radio 버튼을 통해 금융 상품 종류를 선택
            product_type = st.radio(
                '추천받을 금융 상품 종류를 선택하세요:', # 라벨 추가 2024-10-13
                ('적용안함', '예금', '적금', '예금 & 적금'), # 선택 가능한 옵션
                index=('적용안함', '예금', '적금', '예금 & 적금').index(st.session_state['product_type']),  # 기본값 유지
                label_visibility="collapsed"
            )

            # 선택한 상품 종류를 세션 상태에 저장
            st.session_state['product_type'] = product_type

            # 현재 선택된 금융 상품 종류를 화면에 표시
            st.write(f"선택한 금융상품: {st.session_state['product_type']}")
