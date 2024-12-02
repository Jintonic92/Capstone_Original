import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import streamlit as st

class Sidebar:

    @staticmethod
    def reset_chat_button():
        """
        Display the "Reset Chat" button in the sidebar.
        """
        if st.button("Reset chat"):
            st.session_state["reset_chat"] = True
        st.session_state.setdefault("reset_chat", False)

    @staticmethod
    def gather_user_inputs():
        """
        Collect user inputs for target period, installation amount, and keywords.
        """
        with st.sidebar:
            st.header("User Preferences")

            # Target period
            target_period = st.selectbox(
                "Target Saving Period:",
                ["6 months", "1 year", "3 years", "5 years"],
                help="Select the desired saving or deposit duration."
            )

            # Installation amount
            installation_amount = st.number_input(
                "Monthly/Yearly Saving Amount (KRW):",
                min_value=1,
                step=1,
                help="Enter the amount you'd like to save per month or year."
            )

            # Keywords
            keywords = st.text_input(
                "Keywords (e.g., 군인, 여행):",
                help="Enter keywords to refine recommendations."
            )

            # Store inputs in session state
            st.session_state["target_period"] = target_period
            st.session_state["installation_amount"] = installation_amount
            st.session_state["keywords"] = keywords

            # Debugging print statements for development
            print(f"Target Period: {target_period}")
            print(f"Installation Amount: {installation_amount}")
            print(f"Keywords: {keywords}")

    def show_options(self):
        """
        Display reset chat options in an expandable section in the sidebar.
        """
        with st.sidebar.expander("🛠️ Reset Chat", expanded=False):
            self.reset_chat_button()
