import streamlit as st

def user_message(message):
    st.markdown(
        f'<div class="user-message" style="display: flex; justify-content: flex-end; padding: 5px;">'
        f'<div style="background-color: #196b1c; color: white; padding: 10px; border-radius: 10px; font-size:18px; margin-bottom:10px; margin-left:20px;">{message}</div>'
        f'</div>', unsafe_allow_html=True
    )

def bot_message(message):
    st.markdown(
        f'<div class="bot-message" style="display: flex; padding: 5px;">'
        f'<div style="background-color: #074c85; color: white; padding: 10px; border-radius: 10px; font-size:18px; margin-bottom:10px; margin-right:20px;">{message}</div>'
        f'</div>', unsafe_allow_html=True
    )
