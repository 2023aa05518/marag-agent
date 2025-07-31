

import streamlit as st
from session_manager import SessionManager
from database import Database
from api_client import ApiClient
from sidebar_manager import SidebarManager
from chat_ui import ChatUI

DB_FILE = 'db.json'
API_URL = "http://localhost:8100/api/v1/query"

def main():
    st.title("Chat-Interface")
    db = Database(DB_FILE)
    session_manager = SessionManager(st.session_state)
    client = ApiClient(API_URL)
    SidebarManager(session_manager).render()
    ChatUI(client, db, session_manager).render()

if __name__ == "__main__":
    main()
