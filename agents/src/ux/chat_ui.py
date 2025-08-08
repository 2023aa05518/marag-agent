import streamlit as st
from ui_components import user_message, bot_message

class ChatUI:
    def __init__(self, client, db, session_manager):
        self.client = client
        self.db = db
        self.session_manager = session_manager

    def _render_metadata(self, metadata):
        """Display metadata in an expandable section."""
        with st.expander("📊 Response Details", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if 'execution_time_seconds' in metadata:
                    st.metric("⏱️ Execution Time", f"{metadata['execution_time_seconds']:.2f}s")
                if 'total_chunks' in metadata:
                    st.metric("📄 Chunks Processed", metadata['total_chunks'])
            
            with col2:
                if 'k_results' in metadata:
                    st.metric("🔍 Results Retrieved", metadata['k_results'])
                if 'tools_available' in metadata:
                    st.metric("🛠️ Tools Available", metadata['tools_available'])
            
            # Compact display for agents, collection, and sources
            info_items = []
            
            if 'agents_used' in metadata and metadata['agents_used']:
                agents_list = ", ".join([agent.replace('_', ' ').title() for agent in metadata['agents_used']])
                info_items.append(f"**🤖 Agents Used:** {agents_list}")
            
            if 'collection_name' in metadata:
                info_items.append(f"**📚 Collection:** {metadata['collection_name']}")
            
            if 'sources' in metadata and metadata['sources']:
                sources_text = "; ".join([f"{source['document_name']} (Page {source['page_number']})" 
                                        for source in metadata['sources']])
                info_items.append(f"**📄 Sources:** {sources_text}")
            
            # Display all info items as a single markdown block
            if info_items:
                st.markdown("<br>".join(info_items), unsafe_allow_html=True)

    def _extract_sources_from_response(self, response_text):
        """Extract sources from response text and return clean text and sources."""
        import re
        
        if "Sources:" not in response_text:
            return response_text, []
        
        # Split at Sources: and get the clean response
        parts = response_text.split("Sources:", 1)
        clean_response = parts[0].strip()
        sources_section = parts[1].strip() if len(parts) > 1 else ""
        
        # Extract individual sources using regex
        sources = []
        pattern = r'\[Document:\s*([^,]+),\s*Page:\s*([^\]]+)\]'
        matches = re.findall(pattern, sources_section)
        
        for doc_name, page_num in matches:
            sources.append({
                "document_name": doc_name.strip(),
                "page_number": page_num.strip()
            })
        
        return clean_response, sources

    def render(self):
        current_session_id = self.session_manager.state['current_session']
        if current_session_id is None:
            st.info("Click 'New Question' in the sidebar to start a conversation")
            return

        current_session = self.session_manager.state['sessions'][current_session_id]

        # Display chat messages
        for message in current_session['messages']:
            if message['role'] == 'user':
                user_message(message['content'])
            else:
                bot_message(message['content'])
                # Display metadata if available for assistant messages
                if 'metadata' in message and message['metadata']:
                    self._render_metadata(message['metadata'])

        # Chat input
        prompt = st.chat_input("You:")
        if prompt:
            # Auto-name session if this is the first message
            is_first_message = len(current_session['messages']) == 0
            if is_first_message:
                self.session_manager.auto_name_session(current_session_id, prompt)
            
            current_session['messages'].append({'role': 'user', 'content': prompt})
            user_message(prompt)
            try:
                response_data = self.client.get_response(prompt)
                response_text = response_data.get("result", "[No result found]")
                metadata = response_data.get("metadata")
                
                # Debug: Show raw response in console/logs
                # st.write("**Debug - Raw API Response:**")
                # st.json(response_data)
                
            except Exception as e:
                st.error(f"API error: {e}")
                response_text = "[Error: Could not get response from API]"
                metadata = None
            
            bot_message(response_text)
            
            # Display metadata if available
            if metadata:
                self._render_metadata(metadata)
            
            current_session['messages'].append({
                'role': 'assistant', 
                'content': response_text,
                'metadata': metadata
            })
            self.db.db['sessions'] = self.session_manager.state['sessions']
            self.db.save()
            
            # Force UI refresh immediately after first message to update sidebar title
            if is_first_message:
                st.rerun()
