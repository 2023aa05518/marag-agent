import streamlit as st

def user_message(message):
    st.markdown(
        f'<div class="user-message" style="display: flex; justify-content: flex-end; padding: 5px;">'
        f'<div style="background-color: #333; color: white; padding: 10px; border-radius: 10px; font-family: ui-sans-serif, system-ui, -apple-system, \'Segoe UI\', Roboto, sans-serif; font-size: 16px; margin-bottom:10px; margin-left:20px;">{message}</div>'
        f'</div>', unsafe_allow_html=True
    )

def bot_message(message):
    # Convert newlines to HTML line breaks for proper formatting
    formatted_message = message.replace('\n', '<br>')
    st.markdown(
        f'<div class="bot-message" style="display: flex; padding: 5px;">'
        f'<div style="background-color: #333; color: white; padding: 10px; border-radius: 10px; font-family: ui-sans-serif, system-ui, -apple-system, \'Segoe UI\', Roboto, sans-serif; font-size: 16px; margin-bottom:10px; margin-right:20px;">{formatted_message}</div>'
        f'</div>', unsafe_allow_html=True
    )
