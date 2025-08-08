import streamlit as st

class SidebarManager:
    def __init__(self, session_manager):
        self.session_manager = session_manager

    def _render_session_button(self, session_id, session_data):
        if st.sidebar.button(
            session_data['title'],
            key=f"btn_{session_id}",
            use_container_width=True
        ):
            if self.session_manager.state['current_session'] == session_id:
                self.session_manager.state['editing_session'] = session_id
            else:
                self.session_manager.state['current_session'] = session_id
            st.rerun()

    def _render_rename_input(self, session_id, session_data):
        new_title = st.sidebar.text_input(
            "Rename chat",
            value=session_data['title'],
            key=f"edit_{session_id}",
            on_change=lambda: self.session_manager.state.update({'editing_session': None}),
            label_visibility="collapsed"
        )
        if new_title and new_title != session_data['title']:
            self.session_manager.rename_session(session_id, new_title)
            st.rerun()

    def render(self):
        st.sidebar.title("Chat Sessions")
        if st.sidebar.button("➕ New Question"):
            self.session_manager.create_new_session()
            st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.subheader("Recent Chats")
        for session_id, session_data in self.session_manager.state['sessions'].items():
            if self.session_manager.state['editing_session'] == session_id:
                self._render_rename_input(session_id, session_data)
            else:
                self._render_session_button(session_id, session_data)
