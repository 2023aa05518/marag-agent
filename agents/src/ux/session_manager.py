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
            'title': "New Chat",
            'auto_named': False
        }
        self.state['current_session'] = session_id

    def rename_session(self, session_id, new_title):
        self.state['sessions'][session_id]['title'] = new_title

    def auto_name_session(self, session_id, first_question):
        """Auto-name session based on first question if not manually renamed."""
        if session_id in self.state['sessions'] and not self.state['sessions'][session_id].get('auto_named', False):
            title = self._generate_session_title(first_question)
            self.state['sessions'][session_id]['title'] = title
            self.state['sessions'][session_id]['auto_named'] = True

    def _generate_session_title(self, question: str) -> str:
        """Generate a meaningful title from the first question."""
        if not question or len(question.strip()) < 5:
            return "New Chat"
        
        # Remove common question words and clean up
        stop_words = {'how', 'what', 'where', 'when', 'why', 'who', 'can', 'could', 
                      'would', 'should', 'is', 'are', 'do', 'does', 'the', 'a', 'an'}
        
        words = question.strip().replace('?', '').split()[:6]  # First 6 words max
        filtered_words = [word.capitalize() for word in words 
                          if word.lower() not in stop_words and len(word) > 2]
        
        if not filtered_words:
            return question[:30] + "..." if len(question) > 30 else question
        
        title = " ".join(filtered_words[:4])  # Max 4 meaningful words
        return title[:40] + "..." if len(title) > 40 else title

    def get_current_session(self):
        if self.state['current_session']:
            return self.state['sessions'][self.state['current_session']]
        return None
