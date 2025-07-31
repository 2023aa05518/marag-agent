class SessionManager:
    def __init__(self, st_session_state):
        self.state = st_session_state
        self.init_state()

    def init_state(self):
        if 'sessions' not in self.state:
            self.state['sessions'] = {}
        if 'current_session' not in self.state:
            self.state['current_session'] = None
        if 'editing_session' not in self.state:
            self.state['editing_session'] = None

    def create_new_session(self):
        from datetime import datetime
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.state['sessions'][session_id] = {
            'messages': [],
            'title': f"Chat {len(self.state['sessions']) + 1}"
        }
        self.state['current_session'] = session_id

    def rename_session(self, session_id, new_title):
        self.state['sessions'][session_id]['title'] = new_title

    def get_current_session(self):
        if self.state['current_session']:
            return self.state['sessions'][self.state['current_session']]
        return None
