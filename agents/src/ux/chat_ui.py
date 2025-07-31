import streamlit as st
from ui_components import user_message, bot_message

class ChatUI:
    def __init__(self, client, db, session_manager):
        self.client = client
        self.db = db
        self.session_manager = session_manager

    def render(self):
        current_session_id = self.session_manager.state['current_session']
        if current_session_id is None:
            st.info("Click 'New Chat' in the sidebar to start a conversation")
            return

        current_session = self.session_manager.state['sessions'][current_session_id]

        # Display chat messages
        for message in current_session['messages']:
            if message['role'] == 'user':
                user_message(message['content'])
            else:
                bot_message(message['content'])

        # Chat input
        prompt = st.chat_input("You:")
        if prompt:
            current_session['messages'].append({'role': 'user', 'content': prompt})
            user_message(prompt)
            try:
                response_text = self.client.get_response(prompt)
            except Exception as e:
                st.error(f"API error: {e}")
                response_text = "[Error: Could not get response from API]"
            bot_message(response_text)
            current_session['messages'].append({'role': 'assistant', 'content': response_text})
            self.db.db['sessions'] = self.session_manager.state['sessions']
            self.db.save()
