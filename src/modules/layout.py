import streamlit as st

class Layout:

    def show_api_key_missing(self):
        """
        Display an error message when the API key is missing.
        """
        st.markdown(
            """
            <div style='text-align: center;'>
                <h4> System Error: Please set up your API key in the .env file to start chatting.</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def show_header(self, product_names):
        """
        Display the app header.
        """
        st.markdown(
            f"""
            <h1 style='text-align: center; color: lightblue;'> Save Mate에게 {product_names} 추천받으세요! 😁</h1>
            """,
            unsafe_allow_html=True,
        )

    def prompt_form(self):
        """
        Display the form for collecting user inputs.
        """
        with st.form(key="input_form", clear_on_submit=True):
            # Target period
            target_period = st.selectbox(
                "Target Saving Period:",
                ["6 months", "1 year", "3 years", "5 years"],
                help="Select the desired saving or deposit duration.",
            )

            # Installation amount
            installation_amount = st.number_input(
                "Monthly/Yearly Saving Amount (KRW):",
                min_value=1,
                step=1,
                help="Enter the amount you'd like to save per month or year.",
            )

            # Keywords
            keywords = st.text_input(
                "Keywords (e.g., 군인, 여행):",
                help="Enter keywords to refine recommendations.",
            )

            # User query
            user_input = st.text_area(
                "Ask Save Mate:",
                placeholder="Enter your question or preference.",
                key="input",
                label_visibility="collapsed",
            )

            # Submit button
            submit_button = st.form_submit_button(label="Send")

            # Debugging print statements for development
            print(f"Submit button clicked: {submit_button}")
            print(f"User input: {user_input}")

        return submit_button, target_period, installation_amount, keywords, user_input
