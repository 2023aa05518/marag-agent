class ChatManager:
    def __init__(self, session_state):
        if "chat_history" not in session_state:
            session_state.chat_history = []
        self.session_state = session_state

    def add_user_message(self, message):
        self.session_state.chat_history.append((message, False))

    def add_bot_message(self, message):
        self.session_state.chat_history.append((message, True))

    def get_history(self):
        return self.session_state.chat_history
